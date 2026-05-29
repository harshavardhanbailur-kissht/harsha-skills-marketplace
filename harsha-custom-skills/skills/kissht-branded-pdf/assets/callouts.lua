-- Kissht house-style filter.
-- 1. Maps fenced Divs ::: {.summary}/.note/.warn  ->  tcolorbox callout boxes.
-- 2. Shades the header row of every table with the light brand colour.
-- Only runs for the LaTeX/PDF writer.

if FORMAT ~= 'latex' and FORMAT ~= 'beamer' then
  return {}
end

local function pick_class(el)
  for _, c in ipairs(el.classes) do
    if c == 'summary' or c == 'note' or c == 'warn' then return c end
  end
  return nil
end

-- Escape LaTeX specials in the callout title (it is injected raw into \begin{box}{...}).
local function tex_escape(s)
  s = s:gsub('\\', '\\textbackslash{}')
  s = s:gsub('([&%%$#_{}])', '\\%1')
  s = s:gsub('~', '\\textasciitilde{}')
  s = s:gsub('%^', '\\textasciicircum{}')
  return s
end

function Div(el)
  local cls = pick_class(el)
  if not cls then return nil end
  local defaults = { summary = 'Summary', note = 'Note', warn = 'Heads up' }
  local title = tex_escape(el.attributes.title or defaults[cls])
  local env = cls .. 'box'
  local out = { pandoc.RawBlock('latex', '\\begin{' .. env .. '}{' .. title .. '}') }
  for _, b in ipairs(el.content) do out[#out + 1] = b end
  out[#out + 1] = pandoc.RawBlock('latex', '\\end{' .. env .. '}')
  return out
end

-- Shade header cells by prepending \cellcolor{brandlite} to the first block of
-- each header cell. Works regardless of pandoc's table layout (no fragile
-- \rowcolor positioning) and supports both the modern (>=2.10) and legacy (2.9)
-- table representations.
local tint = function() return pandoc.RawInline('latex', '\\cellcolor{brandlite}') end

local function shade_blocks(blocks)
  local first = blocks[1]
  if first and (first.t == 'Plain' or first.t == 'Para') then
    table.insert(first.content, 1, tint())
  else
    table.insert(blocks, 1, pandoc.Plain({ tint() }))
  end
end

function Table(t)
  if t.head and t.head.rows then              -- pandoc >= 2.10
    for _, row in ipairs(t.head.rows) do
      for _, cell in ipairs(row.cells) do shade_blocks(cell.contents) end
    end
  elseif t.headers then                       -- pandoc 2.9 (Cowork sandbox)
    for _, cell in ipairs(t.headers) do shade_blocks(cell) end
  end
  return t
end
