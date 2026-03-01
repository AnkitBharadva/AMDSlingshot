# AI Execution Agent - Process Flow & Use Case Diagrams

## 1. High-Level Process Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          USER INTERACTION                            │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │  User Opens Gmail Email │
                    └─────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │ Clicks "Run Agent" Btn  │
                    └─────────────────────────┘
                                  │
┌─────────────────────────────────────────────────────────────────────┐
│                      CHROME EXTENSION LAYER                          │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │  Extract Email Content  │
                    │  - Subject              │
                    │  - Body                 │
                    │  - Sender               │
                    │  - Timestamp            │
                    │  - Threads/Forwards     │
                    └─────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │  Show Loading State     │
                    └─────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │  POST /run-agent        │
                    │  (HTTPS Request)        │
                    └─────────────────────────┘
                                  │
┌─────────────────────────────────────────────────────────────────────┐
│                        FASTAPI BACKEND                               │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │  Validate Request       │
                    │  (Pydantic Models)      │
                    └─────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │  Task Extraction        │
                    │  Service                │
                    └─────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │  Call LLM API           │
                    │  (OpenAI/Gemini)        │
                    └─────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │  Parse JSON Response    │
                    │  Extract Tasks:         │
                    │  - Title                │
                    │  - Description          │
                    │  - Deadline             │
                    │  - Owner                │
                    │  - Confidence           │
                    └─────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │  Post-Processing        │
                    │  Service                │
                    └─────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │  Assign Priority        │
                    │  (Rule-Based)           │
                    │  - High: < 24h          │
                    │  - Medium: < 7d         │
                    │  - Low: > 7d            │
                    └─────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │  Resolve Deadlines      │
                    │  (python-dateutil)      │
                    └─────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │  Calendar Service       │
                    └─────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │  Fetch Existing Events  │
                    │  (Google Calendar API)  │
                    └─────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │  Find Available Slots   │
                    │  (Deterministic Algo)   │
                    └─────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │  Create Calendar Blocks │
                    │  (30-60 min duration)   │
                    └─────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │  Detect Conflicts       │
                    └─────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │  Meeting Prep Service   │
                    └─────────────────────────┘
                                  │
                                  ▼
            ┌───────────────────┴───────────────────┐
            │                                       │
            ▼                                       ▼
┌─────────────────────┐               ┌─────────────────────┐
│ Is Meeting Task?    │               │ Regular Task        │
│ (Keywords/Context)  │               │ (No Prep Doc)       │
└─────────────────────┘               └─────────────────────┘
            │                                       │
            ▼                                       │
┌─────────────────────┐                           │
│ Generate Prep Doc   │                           │
│ - Context           │                           │
│ - Talking Points    │                           │
│ - Questions         │                           │
│ - Risks             │                           │
└─────────────────────┘                           │
            │                                       │
            └───────────────────┬───────────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │  Build Response         │
                    │  - Tasks                │
                    │  - Stats                │
                    │  - Logs                 │
                    │  - Errors               │
                    └─────────────────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │  Return JSON Response   │
                    └─────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────────┐
│                      CHROME EXTENSION LAYER                          │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │  Receive Response       │
                    └─────────────────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │  Render Task Board UI   │
                    │  - Group by Timeline    │
                    │  - Show Priority        │
                    │  - Display Confidence   │
                    └─────────────────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │  Display Feedback Panel │
                    │  - Statistics           │
                    │  - Execution Logs       │
                    │  - Errors               │
                    └─────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────────┐
│                          USER INTERACTION                            │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
            ┌───────────────────┴───────────────────┐
            │                                       │
            ▼                                       ▼
┌─────────────────────┐               ┌─────────────────────┐
│ Review Tasks        │               │ Adjust/Discard      │
│ - Check Confidence  │               │ - Change Deadline   │
│ - Verify Details    │               │ - Remove Task       │
└─────────────────────┘               └─────────────────────┘
            │                                       │
            └───────────────────┬───────────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │  Export (Optional)      │
                    │  - CSV for Tasks        │
                    │  - PDF for Meeting Prep │
                    └─────────────────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │  View in Google Calendar│
                    └─────────────────────────┘
```


## 2. Detailed Component Interaction Flow

```
┌──────────┐         ┌──────────┐         ┌──────────┐         ┌──────────┐
│  Gmail   │         │  Chrome  │         │  FastAPI │         │  Google  │
│   UI     │         │Extension │         │  Backend │         │ Calendar │
└────┬─────┘         └────┬─────┘         └────┬─────┘         └────┬─────┘
     │                    │                     │                     │
     │ User clicks        │                     │                     │
     │ "Run Agent"        │                     │                     │
     ├───────────────────>│                     │                     │
     │                    │                     │                     │
     │                    │ Extract email       │                     │
     │                    │ content (DOM)       │                     │
     │                    │                     │                     │
     │                    │ POST /run-agent     │                     │
     │                    ├────────────────────>│                     │
     │                    │                     │                     │
     │                    │                     │ Call LLM API        │
     │                    │                     │ (OpenAI/Gemini)     │
     │                    │                     │                     │
     │                    │                     │ Extract tasks       │
     │                    │                     │ with confidence     │
     │                    │                     │                     │
     │                    │                     │ GET /events         │
     │                    │                     ├────────────────────>│
     │                    │                     │                     │
     │                    │                     │ Return events       │
     │                    │                     │<────────────────────┤
     │                    │                     │                     │
     │                    │                     │ Find available      │
     │                    │                     │ time slots          │
     │                    │                     │                     │
     │                    │                     │ POST /events        │
     │                    │                     ├────────────────────>│
     │                    │                     │                     │
     │                    │                     │ Calendar blocks     │
     │                    │                     │ created             │
     │                    │                     │<────────────────────┤
     │                    │                     │                     │
     │                    │ Return tasks +      │                     │
     │                    │ stats + logs        │                     │
     │                    │<────────────────────┤                     │
     │                    │                     │                     │
     │                    │ Render task board   │                     │
     │                    │ and feedback UI     │                     │
     │                    │                     │                     │
     │ Display UI         │                     │                     │
     │<───────────────────┤                     │                     │
     │                    │                     │                     │
     │ User reviews       │                     │                     │
     │ tasks              │                     │                     │
     │                    │                     │                     │
```


## 3. Use Case Diagram

```
                    ┌─────────────────────────────────────────┐
                    │     AI Execution Agent System           │
                    │                                         │
                    │  ┌───────────────────────────────────┐ │
                    │  │  Task Extraction                  │ │
    ┌──────┐        │  │  - Parse email content            │ │
    │      │        │  │  - Extract structured tasks       │ │
    │ User │───────>│  │  - Assign confidence scores       │ │
    │      │        │  └───────────────────────────────────┘ │
    └──────┘        │                                         │
       │            │  ┌───────────────────────────────────┐ │
       │            │  │  Calendar Scheduling              │ │
       │            │  │  - Find available slots           │ │
       └───────────>│  │  - Create calendar blocks         │ │
       │            │  │  - Detect conflicts               │ │
       │            │  └───────────────────────────────────┘ │
       │            │                                         │
       │            │  ┌───────────────────────────────────┐ │
       │            │  │  Meeting Preparation              │ │
       └───────────>│  │  - Detect meeting tasks           │ │
       │            │  │  - Generate prep documents        │ │
       │            │  │  - Extract talking points         │ │
       │            │  └───────────────────────────────────┘ │
       │            │                                         │
       │            │  ┌───────────────────────────────────┐ │
       │            │  │  Task Management                  │ │
       └───────────>│  │  - View task board                │ │
       │            │  │  - Adjust deadlines               │ │
       │            │  │  - Discard tasks                  │ │
       │            │  └───────────────────────────────────┘ │
       │            │                                         │
       │            │  ┌───────────────────────────────────┐ │
       │            │  │  Export & Reporting               │ │
       └───────────>│  │  - Export to CSV                  │ │
                    │  │  - Export to PDF                  │ │
                    │  │  - View statistics                │ │
                    │  └───────────────────────────────────┘ │
                    │                                         │
                    └─────────────────────────────────────────┘
                                    │
                                    │ Uses
                                    ▼
                    ┌─────────────────────────────────────────┐
                    │        External Services                │
                    │                                         │
                    │  ┌──────────┐  ┌──────────┐           │
                    │  │ OpenAI/  │  │  Google  │           │
                    │  │ Gemini   │  │ Calendar │           │
                    │  │   API    │  │   API    │           │
                    │  └──────────┘  └──────────┘           │
                    └─────────────────────────────────────────┘
```


## 4. Detailed Use Case Descriptions

### Use Case 1: Extract Tasks from Email
**Actor**: User  
**Precondition**: User has Gmail open with an email containing action items  
**Main Flow**:
1. User clicks "Run Agent" button
2. System extracts email content (subject, body, sender, timestamp)
3. System sends content to backend API
4. Backend calls LLM API with structured prompt
5. LLM returns JSON with extracted tasks
6. System assigns confidence scores (0.0-1.0)
7. System displays tasks on task board

**Postcondition**: Tasks are extracted and displayed with confidence scores  
**Alternative Flow**: If LLM fails, system returns error message

---

### Use Case 2: Schedule Calendar Blocks
**Actor**: User  
**Precondition**: Tasks have been extracted  
**Main Flow**:
1. System retrieves existing calendar events via Google Calendar API
2. System identifies available time slots
3. For each task with deadline:
   - Find slot before deadline
   - Check for conflicts
   - Create 30-60 minute block
4. System updates task state (scheduled | conflict | manual_review)
5. System displays scheduling results

**Postcondition**: Calendar blocks created for schedulable tasks  
**Alternative Flow**: If conflicts detected, task marked for manual review

---

### Use Case 3: Generate Meeting Preparation Document
**Actor**: User  
**Precondition**: Meeting-related task detected  
**Main Flow**:
1. System detects meeting keywords in task
2. System analyzes email context
3. System generates prep document with:
   - Context summary
   - Talking points
   - Questions to ask
   - Potential risks
4. System attaches prep document to task
5. User can export to PDF

**Postcondition**: Meeting prep document available for export  
**Alternative Flow**: If not a meeting task, skip prep generation

---

### Use Case 4: Adjust Task Deadline
**Actor**: User  
**Precondition**: Tasks displayed on task board  
**Main Flow**:
1. User clicks deadline adjustment button
2. System displays date picker
3. User selects new deadline
4. System updates task deadline
5. System recalculates priority if needed
6. System updates display

**Postcondition**: Task deadline updated  
**Alternative Flow**: User cancels adjustment

---

### Use Case 5: Discard Task
**Actor**: User  
**Precondition**: Tasks displayed on task board  
**Main Flow**:
1. User clicks discard button on task
2. System removes task from display
3. If calendar block exists, system optionally deletes it
4. System updates statistics

**Postcondition**: Task removed from task board  
**Alternative Flow**: None

---

### Use Case 6: Export Tasks to CSV
**Actor**: User  
**Precondition**: Tasks have been extracted  
**Main Flow**:
1. User clicks "Export to CSV" button
2. System formats tasks as CSV with columns:
   - Title, Description, Deadline, Owner, Priority, Confidence, State
3. System triggers browser download
4. User saves CSV file

**Postcondition**: CSV file downloaded  
**Alternative Flow**: None

---

### Use Case 7: View Execution Logs
**Actor**: User  
**Precondition**: Agent has been executed  
**Main Flow**:
1. System displays feedback panel
2. User views statistics:
   - Tasks extracted
   - Calendar blocks created
   - Scheduling conflicts
   - Manual review items
3. User views execution logs with timestamps
4. User views any error messages

**Postcondition**: User understands agent execution results  
**Alternative Flow**: None


## 5. State Transition Diagram

```
                    ┌─────────────────┐
                    │   Email Opened  │
                    └────────┬────────┘
                             │
                             │ User clicks "Run Agent"
                             ▼
                    ┌─────────────────┐
                    │   Processing    │
                    │   (Loading)     │
                    └────────┬────────┘
                             │
                             │ LLM extraction complete
                             ▼
                    ┌─────────────────┐
                    │ Tasks Extracted │
                    └────────┬────────┘
                             │
                             │ Calendar scheduling
                             ▼
            ┌────────────────┴────────────────┐
            │                                  │
            ▼                                  ▼
   ┌─────────────────┐              ┌─────────────────┐
   │   Scheduled     │              │ Manual Review   │
   │   (Success)     │              │ (Low Confidence)│
   └─────────────────┘              └─────────────────┘
            │                                  │
            │                                  │
            └────────────────┬─────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Scheduling      │
                    │ Conflict        │
                    └────────┬────────┘
                             │
                             │ User adjusts deadline
                             ▼
                    ┌─────────────────┐
                    │ Rescheduling    │
                    └────────┬────────┘
                             │
                             ▼
            ┌────────────────┴────────────────┐
            │                                  │
            ▼                                  ▼
   ┌─────────────────┐              ┌─────────────────┐
   │   Scheduled     │              │   Discarded     │
   │   (Updated)     │              │   (Removed)     │
   └─────────────────┘              └─────────────────┘
```


## 6. Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Level 0: Context Diagram                     │
└─────────────────────────────────────────────────────────────────────┘

                            ┌──────────┐
                            │   User   │
                            └─────┬────┘
                                  │
                    Email Content │ │ Task Board UI
                                  │ │
                                  ▼ ▼
                    ┌──────────────────────────┐
                    │                          │
                    │   AI Execution Agent     │
                    │                          │
                    └──────────────────────────┘
                         │              │
            LLM Request  │              │  Calendar Events
            LLM Response │              │  Create/Read
                         │              │
                         ▼              ▼
                  ┌──────────┐    ┌──────────┐
                  │ OpenAI/  │    │  Google  │
                  │ Gemini   │    │ Calendar │
                  └──────────┘    └──────────┘


┌─────────────────────────────────────────────────────────────────────┐
│                         Level 1: System Processes                    │
└─────────────────────────────────────────────────────────────────────┘

    ┌──────┐
    │ User │
    └───┬──┘
        │
        │ Email Content
        ▼
┌────────────────┐
│  1.0           │
│  Extract Email │
│  Content       │
└───────┬────────┘
        │
        │ Raw Email Data
        ▼
┌────────────────┐         ┌──────────┐
│  2.0           │────────>│ OpenAI/  │
│  Extract Tasks │<────────│ Gemini   │
│  (LLM)         │         └──────────┘
└───────┬────────┘
        │
        │ Structured Tasks
        ▼
┌────────────────┐
│  3.0           │
│  Assign        │
│  Priority      │
└───────┬────────┘
        │
        │ Prioritized Tasks
        ▼
┌────────────────┐         ┌──────────┐
│  4.0           │────────>│  Google  │
│  Schedule      │<────────│ Calendar │
│  Calendar      │         └──────────┘
└───────┬────────┘
        │
        │ Scheduled Tasks
        ▼
┌────────────────┐
│  5.0           │
│  Generate      │
│  Meeting Prep  │
└───────┬────────┘
        │
        │ Complete Task Data
        ▼
┌────────────────┐
│  6.0           │
│  Render UI     │
└───────┬────────┘
        │
        │ Task Board UI
        ▼
    ┌──────┐
    │ User │
    └──────┘
```


## 7. Decision Flow for Task Processing

```
                    ┌─────────────────┐
                    │  Task Extracted │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Confidence >= 0.7?│
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
                 Yes│                 │No
                    │                 │
                    ▼                 ▼
          ┌─────────────────┐  ┌─────────────────┐
          │ Proceed to      │  │ Mark for        │
          │ Scheduling      │  │ Manual Review   │
          └────────┬────────┘  └─────────────────┘
                   │
                   ▼
          ┌─────────────────┐
          │ Has Deadline?   │
          └────────┬────────┘
                   │
          ┌────────┴────────┐
          │                 │
       Yes│                 │No
          │                 │
          ▼                 ▼
┌─────────────────┐  ┌─────────────────┐
│ Find Available  │  │ Skip Calendar   │
│ Time Slot       │  │ Scheduling      │
└────────┬────────┘  └─────────────────┘
         │
         ▼
┌─────────────────┐
│ Slot Available? │
└────────┬────────┘
         │
┌────────┴────────┐
│                 │
Yes│              │No
│                 │
▼                 ▼
┌─────────────────┐  ┌─────────────────┐
│ Create Calendar │  │ Mark Scheduling │
│ Block           │  │ Conflict        │
└────────┬────────┘  └─────────────────┘
         │
         ▼
┌─────────────────┐
│ Is Meeting Task?│
└────────┬────────┘
         │
┌────────┴────────┐
│                 │
Yes│              │No
│                 │
▼                 ▼
┌─────────────────┐  ┌─────────────────┐
│ Generate        │  │ Task Complete   │
│ Meeting Prep    │  │                 │
└────────┬────────┘  └─────────────────┘
         │
         ▼
┌─────────────────┐
│ Task Complete   │
└─────────────────┘
```


## 8. Actor-System Interaction (Use Case View)

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│                        System Boundary                               │
│                                                                      │
│                                                                      │
│    ┌──────────────────────────────────────────────────┐            │
│    │                                                  │            │
│    │  «use case»                                      │            │
│    │  Extract Tasks from Email                        │            │
│    │                                                  │            │
│    │  - Parse email content                           │            │
│    │  - Call LLM API                                  │            │
│    │  - Assign confidence scores                      │            │
│    │                                                  │            │
│    └──────────────────────────────────────────────────┘            │
│                          │                                          │
│                          │ «include»                                │
│                          ▼                                          │
│    ┌──────────────────────────────────────────────────┐            │
│    │                                                  │            │
│    │  «use case»                                      │            │
│    │  Assign Priority                                 │            │
│    │                                                  │            │
│    │  - Apply rule-based logic                        │            │
│    │  - Consider deadline urgency                     │            │
│    │  - Check for urgent keywords                     │            │
│    │                                                  │            │
│    └──────────────────────────────────────────────────┘            │
│                          │                                          │
│                          │ «include»                                │
│                          ▼                                          │
│    ┌──────────────────────────────────────────────────┐            │
│    │                                                  │            │
│    │  «use case»                                      │            │
│    │  Schedule Calendar Blocks                        │            │
│    │                                                  │            │
│    │  - Fetch existing events                         │            │
│    │  - Find available slots                          │            │
│    │  - Create calendar blocks                        │            │
│    │  - Detect conflicts                              │            │
│    │                                                  │            │
│    └──────────────────────────────────────────────────┘            │
│                          │                                          │
│                          │ «extend»                                 │
│                          ▼                                          │
│    ┌──────────────────────────────────────────────────┐            │
│    │                                                  │            │
│    │  «use case»                                      │            │
│    │  Generate Meeting Prep                           │            │
│    │                                                  │            │
│    │  - Detect meeting keywords                       │            │
│    │  - Extract context                               │            │
│    │  - Generate talking points                       │            │
│    │  - Identify risks                                │            │
│    │                                                  │            │
│    └──────────────────────────────────────────────────┘            │
│                                                                      │
│                                                                      │
│    ┌──────────────────────────────────────────────────┐            │
│    │                                                  │            │
│    │  «use case»                                      │            │
│    │  Manage Tasks                                    │            │
│    │                                                  │            │
│    │  - View task board                               │            │
│    │  - Adjust deadlines                              │            │
│    │  - Discard tasks                                 │            │
│    │  - Review confidence scores                      │            │
│    │                                                  │            │
│    └──────────────────────────────────────────────────┘            │
│                                                                      │
│                                                                      │
│    ┌──────────────────────────────────────────────────┐            │
│    │                                                  │            │
│    │  «use case»                                      │            │
│    │  Export Data                                     │            │
│    │                                                  │            │
│    │  - Export tasks to CSV                           │            │
│    │  - Export meeting prep to PDF                    │            │
│    │  - View execution logs                           │            │
│    │                                                  │            │
│    └──────────────────────────────────────────────────┘            │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
         ▲                                              ▲
         │                                              │
         │                                              │
    ┌────┴────┐                                   ┌─────┴──────┐
    │         │                                   │            │
    │  User   │                                   │  External  │
    │         │                                   │  Services  │
    └─────────┘                                   │  (LLM,     │
                                                  │  Calendar) │
                                                  └────────────┘
```


## 9. Error Handling Flow

```
                    ┌─────────────────┐
                    │  User Action    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  API Request    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Validate Input │
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
                Valid│                │Invalid
                    │                 │
                    ▼                 ▼
          ┌─────────────────┐  ┌─────────────────┐
          │ Process Request │  │ Return 400      │
          │                 │  │ Bad Request     │
          └────────┬────────┘  └─────────────────┘
                   │
                   ▼
          ┌─────────────────┐
          │ Call LLM API    │
          └────────┬────────┘
                   │
          ┌────────┴────────┐
          │                 │
      Success│              │Failure
          │                 │
          ▼                 ▼
┌─────────────────┐  ┌─────────────────┐
│ Parse Response  │  │ Log Error       │
│                 │  │ Return 502      │
└────────┬────────┘  │ Bad Gateway     │
         │           └─────────────────┘
         ▼
┌─────────────────┐
│ Call Calendar   │
│ API             │
└────────┬────────┘
         │
┌────────┴────────┐
│                 │
Success│          │Failure
│                 │
▼                 ▼
┌─────────────────┐  ┌─────────────────┐
│ Return Success  │  │ Partial Success │
│ Response        │  │ (Tasks extracted│
│                 │  │ but not         │
│                 │  │ scheduled)      │
└─────────────────┘  └─────────────────┘
```

## 10. Summary of Key Flows

### Primary Success Flow
1. User opens email → Clicks "Run Agent"
2. Extension extracts email content
3. Backend calls LLM → Extracts tasks with confidence
4. Backend assigns priority based on rules
5. Backend schedules calendar blocks
6. Backend generates meeting prep (if applicable)
7. Extension renders task board + feedback
8. User reviews and adjusts as needed

### Alternative Flows
- **Low Confidence**: Task marked for manual review instead of auto-scheduling
- **Scheduling Conflict**: Task flagged, user must resolve manually
- **LLM Failure**: Error message displayed, no tasks extracted
- **Calendar API Failure**: Tasks extracted but not scheduled
- **No Deadline**: Task extracted but not scheduled on calendar

### Error Recovery
- **API Timeout**: Retry with exponential backoff
- **Invalid Response**: Log error, return user-friendly message
- **Partial Failure**: Return partial results with error details
- **Network Error**: Display offline message, suggest retry

