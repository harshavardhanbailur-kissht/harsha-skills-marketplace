# Notion Database Schema: PRD Decomposition

## Database Configuration

### Database Title
"PRD Decomposition — {PRD Name}"

### Properties Schema (for notion-create-database)

```json
{
  "properties": {
    "Item Type": {
      "type": "select",
      "select": {
        "options": [
          {"name": "Epic", "color": "purple"},
          {"name": "Feature", "color": "blue"},
          {"name": "Task", "color": "green"}
        ]
      }
    },
    "Item ID": {
      "type": "rich_text",
      "rich_text": {}
    },
    "Status": {
      "type": "select",
      "select": {
        "options": [
          {"name": "Not Started", "color": "default"},
          {"name": "In Progress", "color": "blue"},
          {"name": "Done", "color": "green"},
          {"name": "Blocked", "color": "red"}
        ]
      }
    },
    "Priority": {
      "type": "select",
      "select": {
        "options": [
          {"name": "P0 - Critical", "color": "red"},
          {"name": "P1 - High", "color": "orange"},
          {"name": "P2 - Medium", "color": "yellow"},
          {"name": "P3 - Low", "color": "default"}
        ]
      }
    },
    "Effort": {
      "type": "select",
      "select": {
        "options": [
          {"name": "XS", "color": "default"},
          {"name": "S", "color": "green"},
          {"name": "M", "color": "yellow"},
          {"name": "L", "color": "orange"},
          {"name": "XL", "color": "red"}
        ]
      }
    },
    "Domain": {
      "type": "multi_select",
      "multi_select": {
        "options": [
          {"name": "Frontend", "color": "blue"},
          {"name": "Backend", "color": "green"},
          {"name": "Infrastructure", "color": "orange"},
          {"name": "Data", "color": "purple"},
          {"name": "ML/AI", "color": "pink"},
          {"name": "Security", "color": "red"},
          {"name": "Compliance", "color": "yellow"}
        ]
      }
    },
    "Execution Layer": {
      "type": "number",
      "number": {"format": "number"}
    },
    "Critical Path": {
      "type": "checkbox",
      "checkbox": {}
    },
    "PRD Requirements": {
      "type": "rich_text",
      "rich_text": {}
    },
    "Dependencies": {
      "type": "rich_text",
      "rich_text": {}
    },
    "Acceptance Criteria": {
      "type": "rich_text",
      "rich_text": {}
    }
  }
}
```

### Creating Pages (for notion-create-pages)

#### Epic Page Example
```json
{
  "parent": {"data_source_id": "{data_source_id}"},
  "pages": [{
    "properties": {
      "Name": "E-1: [Auth] — User Authentication System",
      "Item Type": "Epic",
      "Item ID": "E-1",
      "Status": "Not Started",
      "Priority": "P0 - Critical",
      "Effort": "XL",
      "Domain": "Backend, Security",
      "Execution Layer": 0,
      "Critical Path": "__YES__",
      "PRD Requirements": "REQ-001, REQ-002, REQ-003"
    },
    "content": "## Overview\n{epic description}\n\n## Features\n- F-1.1: ...\n- F-1.2: ..."
  }]
}
```

#### Task Page Example
```json
{
  "parent": {"data_source_id": "{data_source_id}"},
  "pages": [{
    "properties": {
      "Name": "T-1.1.1: Create User model with SQLAlchemy",
      "Item Type": "Task",
      "Item ID": "T-1.1.1",
      "Status": "Not Started",
      "Priority": "P0 - Critical",
      "Effort": "M",
      "Domain": "Backend, Data",
      "Execution Layer": 0,
      "Critical Path": "__YES__",
      "PRD Requirements": "REQ-001",
      "Dependencies": "None",
      "Acceptance Criteria": "Given a valid user payload, when POST /users is called, then a new user record is created in the database"
    },
    "content": "## Objective\n{task objective}\n\n## Technical Requirements\n{tech details}\n\n## Boundary Conditions\n{what not to do}\n\n## Verification\n{how to verify}"
  }]
}
```

### Recommended Views
1. **Board View**: Group by Status, Filter by Item Type = Task
2. **Table View**: Sort by Execution Layer, then Priority
3. **Timeline View**: Effort as duration (if using date properties)
4. **Board by Epic**: Group by Parent relation, filter by Item Type = Task
