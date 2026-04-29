# Web App Template Specification

## HTML Shell Structure

```html
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{COURSE_TITLE}} - Interactive Learning Guide</title>
  <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          fontFamily: { sans: ['Inter', 'system-ui', 'sans-serif'] }
        }
      }
    }
  </script>
</head>
<body class="bg-slate-900 text-slate-50 font-sans">
  <div id="root"></div>
  <script type="text/babel">
    // Course data embedded here
    const COURSE_DATA = {{COURSE_JSON}};
    
    // React App code here
    // ...
  </script>
</body>
</html>
```

## Component Templates

### Sidebar Module Item
```jsx
function ModuleItem({ module, currentLessonId, completedLessons, onLessonClick }) {
  const [expanded, setExpanded] = useState(false);
  const completedCount = module.lessons.filter(l => completedLessons.has(l.id)).length;
  
  return (
    <div className="mb-2">
      <button onClick={() => setExpanded(!expanded)} 
        className="w-full flex items-center justify-between px-3 py-2 rounded-lg hover:bg-slate-700 text-left">
        <span className="font-medium text-sm">{module.title}</span>
        <span className="text-xs text-slate-400">{completedCount}/{module.lessons.length}</span>
      </button>
      {expanded && (
        <div className="ml-4 mt-1 space-y-1">
          {module.lessons.map(lesson => (
            <button key={lesson.id} onClick={() => onLessonClick(lesson.id)}
              className={`w-full text-left px-3 py-1.5 rounded text-sm flex items-center gap-2
                ${currentLessonId === lesson.id ? 'bg-blue-600/20 text-blue-400' : 'hover:bg-slate-700 text-slate-300'}`}>
              {completedLessons.has(lesson.id) ? '✓' : '○'} {lesson.title}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
```

### MCQ Component
```jsx
function MCQQuestion({ mcq, index, onAnswer, existingAnswer }) {
  const [selected, setSelected] = useState(existingAnswer?.selected ?? null);
  const [submitted, setSubmitted] = useState(!!existingAnswer);
  const [hintsRevealed, setHintsRevealed] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  
  const handleSubmit = () => {
    if (selected === null) return;
    setSubmitted(true);
    onAnswer(index, { selected, correct: selected === mcq.correctAnswer, hintsUsed: hintsRevealed, shownAnswer: showAnswer });
  };

  return (
    <div className="bg-slate-800 rounded-xl p-6 my-4">
      <p className="font-medium mb-4">Q{index + 1}: {mcq.question}</p>
      <div className="space-y-2">
        {mcq.options.map((option, i) => {
          let optionClass = "border border-slate-600 rounded-lg px-4 py-3 cursor-pointer transition-all";
          if (submitted) {
            if (i === mcq.correctAnswer) optionClass += " border-green-500 bg-green-900/20";
            else if (i === selected) optionClass += " border-red-500 bg-red-900/20";
          } else if (i === selected) {
            optionClass += " border-blue-500 bg-blue-900/20";
          } else {
            optionClass += " hover:border-slate-400";
          }
          return (
            <button key={i} onClick={() => !submitted && setSelected(i)} className={`w-full text-left ${optionClass}`}>
              {String.fromCharCode(65 + i)}. {option}
            </button>
          );
        })}
      </div>
      
      {/* Submit / Feedback */}
      {!submitted && <button onClick={handleSubmit} disabled={selected === null}
        className="mt-4 px-6 py-2 bg-blue-600 rounded-lg disabled:opacity-50">Check Answer</button>}
      
      {submitted && (
        <div className={`mt-4 p-4 rounded-lg ${selected === mcq.correctAnswer ? 'bg-green-900/20 border border-green-700' : 'bg-red-900/20 border border-red-700'}`}>
          {selected === mcq.correctAnswer 
            ? <p className="text-green-400 font-medium">✓ Correct!</p>
            : <p className="text-red-400 font-medium">✗ Incorrect</p>}
          <p className="mt-2 text-slate-300">{mcq.explanation}</p>
          {selected !== mcq.correctAnswer && mcq.wrongExplanations?.[String(selected)] && (
            <p className="mt-2 text-slate-400 italic">Why your answer was wrong: {mcq.wrongExplanations[String(selected)]}</p>
          )}
        </div>
      )}
      
      {/* Hints */}
      {!submitted && mcq.hints?.length > 0 && (
        <div className="mt-3">
          <button onClick={() => setHintsRevealed(Math.min(hintsRevealed + 1, mcq.hints.length))}
            className="text-violet-400 text-sm hover:underline">
            {hintsRevealed === 0 ? '💡 Need a hint?' : hintsRevealed < mcq.hints.length ? 'Show another hint' : 'No more hints'}
          </button>
          {mcq.hints.slice(0, hintsRevealed).map((hint, i) => (
            <div key={i} className="mt-2 ml-4 p-3 bg-violet-900/20 border-l-2 border-violet-500 rounded-r text-sm text-violet-300">
              Hint {i + 1}: {hint}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

### Tip Box Component
```jsx
function TipBox({ type, children }) {
  const styles = {
    tip: { bg: 'bg-amber-900/20', border: 'border-amber-500', label: '💡 Pro Tip', labelColor: 'text-amber-400' },
    warning: { bg: 'bg-red-900/20', border: 'border-red-500', label: '⚠️ Common Mistake', labelColor: 'text-red-400' },
    remember: { bg: 'bg-blue-900/20', border: 'border-blue-500', label: '📌 Remember', labelColor: 'text-blue-400' },
    info: { bg: 'bg-cyan-900/20', border: 'border-cyan-500', label: 'ℹ️ Note', labelColor: 'text-cyan-400' }
  };
  const s = styles[type] || styles.info;
  return (
    <div className={`${s.bg} border-l-4 ${s.border} p-4 rounded-r my-4`}>
      <span className={`font-bold ${s.labelColor}`}>{s.label}</span>
      <p className="mt-1 text-slate-300">{children}</p>
    </div>
  );
}
```

## Responsive Breakpoints

- **Desktop (>1024px)**: Sidebar visible + main content
- **Tablet (768-1024px)**: Sidebar overlay + main content full width
- **Mobile (<768px)**: Sidebar as slide-out drawer + full width content

## Animation Suggestions

Keep minimal — focus on UX, not flashiness:
- Hint reveal: `transition-all duration-200` slide down
- MCQ feedback: `transition-colors duration-150`
- Sidebar collapse: `transition-transform duration-200`
- Progress bar: `transition-all duration-500 ease-out`
