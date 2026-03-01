# AI Execution Agent - Wireframes & Mock Diagrams

## 1. Gmail Interface with "Run Agent" Button

```
┌────────────────────────────────────────────────────────────────────────┐
│ Gmail                                                    [User Profile] │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │ ← Back to Inbox                                                  │ │
│  ├──────────────────────────────────────────────────────────────────┤ │
│  │                                                                  │ │
│  │  From: john.doe@company.com                                      │ │
│  │  To: me                                                          │ │
│  │  Subject: Q4 Planning - Action Items                             │ │
│  │  Date: Feb 28, 2026, 10:30 AM                                    │ │
│  │                                                                  │ │
│  │  ┌────────────────────────────────────────────────────────────┐ │ │
│  │  │  🤖 Run Agent                                              │ │ │
│  │  └────────────────────────────────────────────────────────────┘ │ │
│  │                                                                  │ │
│  │  ──────────────────────────────────────────────────────────────  │ │
│  │                                                                  │ │
│  │  Hi Team,                                                        │ │
│  │                                                                  │ │
│  │  Following up on our discussion, please complete:                │ │
│  │                                                                  │ │
│  │  1. Review the Q4 budget proposal by tomorrow                    │ │
│  │  2. Schedule a client meeting for next week                      │ │
│  │  3. Update project timeline by Friday                            │ │
│  │                                                                  │ │
│  │  The budget review is urgent - we need to finalize by EOD        │ │
│  │  tomorrow.                                                       │ │
│  │                                                                  │ │
│  │  Thanks!                                                         │ │
│  │  John                                                            │ │
│  │                                                                  │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```


## 2. Loading State

```
┌────────────────────────────────────────────────────────────────────────┐
│ Gmail                                                    [User Profile] │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │ ← Back to Inbox                                                  │ │
│  ├──────────────────────────────────────────────────────────────────┤ │
│  │                                                                  │ │
│  │  From: john.doe@company.com                                      │ │
│  │  Subject: Q4 Planning - Action Items                             │ │
│  │                                                                  │ │
│  │  ┌────────────────────────────────────────────────────────────┐ │ │
│  │  │  ⏳ Processing...                                          │ │ │
│  │  │                                                            │ │ │
│  │  │  [████████████░░░░░░░░░░░░░░░░░░░░] 40%                   │ │ │
│  │  │                                                            │ │ │
│  │  │  Extracting tasks from email...                           │ │ │
│  │  └────────────────────────────────────────────────────────────┘ │ │
│  │                                                                  │ │
│  │  ──────────────────────────────────────────────────────────────  │ │
│  │                                                                  │ │
│  │  [Email content continues below...]                              │ │
│  │                                                                  │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```


## 3. Task Board Interface (Main View)

```
┌────────────────────────────────────────────────────────────────────────────────────┐
│ Gmail - AI Execution Agent Results                               [User Profile]    │
├────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                    │
│  ┌──────────────────────────────────────────────────────────────────────────────┐ │
│  │ ✅ Agent Execution Complete                                    [Export CSV]  │ │
│  └──────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                    │
│  ┌──────────────────────────────────────────────────────────────────────────────┐ │
│  │                           📊 EXECUTION SUMMARY                               │ │
│  │                                                                              │ │
│  │    Tasks Extracted: 3    Calendar Blocks: 2    Conflicts: 0    Review: 1    │ │
│  │                                                                              │ │
│  └──────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                    │
│  ┌──────────────────────────────────────────────────────────────────────────────┐ │
│  │                              📋 TASK BOARD                                   │ │
│  ├──────────────────────────────────────────────────────────────────────────────┤ │
│  │                                                                              │ │
│  │  ┌─────────────────────────────────────────────────────────────────────┐    │ │
│  │  │ 🔴 TODAY                                                            │    │ │
│  │  ├─────────────────────────────────────────────────────────────────────┤    │ │
│  │  │                                                                     │    │ │
│  │  │  ┌───────────────────────────────────────────────────────────────┐ │    │ │
│  │  │  │ 🔴 HIGH PRIORITY                    Confidence: 95% ✓         │ │    │ │
│  │  │  │                                                               │ │    │ │
│  │  │  │ Review Q4 budget proposal                                     │ │    │ │
│  │  │  │                                                               │ │    │ │
│  │  │  │ 📝 Review and finalize the Q4 budget proposal document        │ │    │ │
│  │  │  │    before end of day tomorrow                                 │ │    │ │
│  │  │  │                                                               │ │    │ │
│  │  │  │ 📅 Deadline: Tomorrow (Feb 29, 2026)                          │ │    │ │
│  │  │  │ 👤 Owner: Team                                                │ │    │ │
│  │  │  │ ✅ Status: Scheduled                                          │ │    │ │
│  │  │  │ 📆 Calendar Block: Tomorrow 2:00 PM - 3:00 PM                 │ │    │ │
│  │  │  │                                                               │ │    │ │
│  │  │  │ 💬 Source: "Review the Q4 budget proposal by tomorrow"        │ │    │ │
│  │  │  │                                                               │ │    │ │
│  │  │  │ [Adjust Deadline]  [Discard Task]  [View in Calendar]        │ │    │ │
│  │  │  └───────────────────────────────────────────────────────────────┘ │    │ │
│  │  │                                                                     │    │ │
│  │  └─────────────────────────────────────────────────────────────────────┘    │ │
│  │                                                                              │ │
│  │  ┌─────────────────────────────────────────────────────────────────────┐    │ │
│  │  │ 🟡 TOMORROW                                                         │    │ │
│  │  ├─────────────────────────────────────────────────────────────────────┤    │ │
│  │  │                                                                     │    │ │
│  │  │  (No tasks)                                                         │    │ │
│  │  │                                                                     │    │ │
│  │  └─────────────────────────────────────────────────────────────────────┘    │ │
│  │                                                                              │ │
│  │  ┌─────────────────────────────────────────────────────────────────────┐    │ │
│  │  │ 🟢 UPCOMING                                                         │    │ │
│  │  ├─────────────────────────────────────────────────────────────────────┤    │ │
│  │  │                                                                     │    │ │
│  │  │  ┌───────────────────────────────────────────────────────────────┐ │    │ │
│  │  │  │ 🟡 MEDIUM PRIORITY                  Confidence: 88% ✓         │ │    │ │
│  │  │  │                                                               │ │    │ │
│  │  │  │ Schedule client meeting                                       │ │    │ │
│  │  │  │                                                               │ │    │ │
│  │  │  │ 📝 Arrange and schedule a meeting with the client             │ │    │ │
│  │  │  │                                                               │ │    │ │
│  │  │  │ 📅 Deadline: Next week (Mar 7, 2026)                          │ │    │ │
│  │  │  │ 👤 Owner: Team                                                │ │    │ │
│  │  │  │ ✅ Status: Scheduled                                          │ │    │ │
│  │  │  │ 📆 Calendar Block: Mar 5, 2026 10:00 AM - 11:00 AM            │ │    │ │
│  │  │  │ 📄 Meeting Prep: Available [Export PDF]                       │ │    │ │
│  │  │  │                                                               │ │    │ │
│  │  │  │ 💬 Source: "Schedule a client meeting for next week"          │ │    │ │
│  │  │  │                                                               │ │    │ │
│  │  │  │ [Adjust Deadline]  [Discard Task]  [View Prep Doc]           │ │    │ │
│  │  │  └───────────────────────────────────────────────────────────────┘ │    │ │
│  │  │                                                                     │    │ │
│  │  │  ┌───────────────────────────────────────────────────────────────┐ │    │ │
│  │  │  │ 🟡 MEDIUM PRIORITY                  Confidence: 65% ⚠️        │ │    │ │
│  │  │  │                                                               │ │    │ │
│  │  │  │ Update project timeline                                       │ │    │ │
│  │  │  │                                                               │ │    │ │
│  │  │  │ 📝 Update and revise the project timeline document            │ │    │ │
│  │  │  │                                                               │ │    │ │
│  │  │  │ 📅 Deadline: Friday (Mar 1, 2026)                             │ │    │ │
│  │  │  │ 👤 Owner: Team                                                │ │    │ │
│  │  │  │ ⚠️  Status: Manual Review Required (Low Confidence)           │ │    │ │
│  │  │  │                                                               │ │    │ │
│  │  │  │ 💬 Source: "Update project timeline by Friday"                │ │    │ │
│  │  │  │                                                               │ │    │ │
│  │  │  │ [Confirm & Schedule]  [Adjust Details]  [Discard Task]       │ │    │ │
│  │  │  └───────────────────────────────────────────────────────────────┘ │    │ │
│  │  │                                                                     │    │ │
│  │  └─────────────────────────────────────────────────────────────────────┘    │ │
│  │                                                                              │ │
│  └──────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                    │
└────────────────────────────────────────────────────────────────────────────────────┘
```


## 4. Feedback Panel (Execution Logs)

```
┌────────────────────────────────────────────────────────────────────────┐
│                        📊 EXECUTION FEEDBACK                           │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  Statistics                                                            │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │                                                                  │ │
│  │  ✅ Tasks Extracted:        3                                    │ │
│  │  📅 Calendar Blocks:        2                                    │ │
│  │  ⚠️  Scheduling Conflicts:  0                                    │ │
│  │  🔍 Manual Review Items:    1                                    │ │
│  │  ⏱️  Processing Time:       12.4 seconds                         │ │
│  │                                                                  │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                        │
│  Execution Logs                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │                                                                  │ │
│  │  [10:45:32] ℹ️  Agent execution started                          │ │
│  │  [10:45:33] ℹ️  Email content extracted (1,247 characters)       │ │
│  │  [10:45:34] ℹ️  Calling LLM API (OpenAI GPT-4)                   │ │
│  │  [10:45:40] ✅ LLM response received                             │ │
│  │  [10:45:40] ✅ Extracted 3 tasks                                 │ │
│  │  [10:45:41] ℹ️  Assigning priorities based on deadlines          │ │
│  │  [10:45:41] ✅ Task 1: HIGH priority (deadline < 24h)            │ │
│  │  [10:45:41] ✅ Task 2: MEDIUM priority (deadline < 7d)           │ │
│  │  [10:45:41] ✅ Task 3: MEDIUM priority (deadline < 7d)           │ │
│  │  [10:45:42] ℹ️  Fetching calendar events from Google Calendar    │ │
│  │  [10:45:43] ✅ Retrieved 15 existing events                      │ │
│  │  [10:45:43] ℹ️  Finding available time slots                     │ │
│  │  [10:45:43] ✅ Task 1: Scheduled for Feb 29, 2:00 PM             │ │
│  │  [10:45:43] ✅ Task 2: Scheduled for Mar 5, 10:00 AM             │ │
│  │  [10:45:44] ⚠️  Task 3: Low confidence (0.65), manual review     │ │
│  │  [10:45:44] ℹ️  Detecting meeting-related tasks                  │ │
│  │  [10:45:44] ✅ Task 2: Meeting detected, generating prep doc     │ │
│  │  [10:45:45] ✅ Meeting prep document generated                   │ │
│  │  [10:45:45] ✅ Agent execution complete                          │ │
│  │                                                                  │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                        │
│  Errors & Warnings                                                     │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │                                                                  │ │
│  │  ⚠️  Warning: Task 3 has low confidence score (0.65)             │ │
│  │     → Please review task details manually                        │ │
│  │                                                                  │ │
│  │  (No errors)                                                     │ │
│  │                                                                  │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                        │
│  [Close]                                                               │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```


## 5. Meeting Preparation Document View

```
┌────────────────────────────────────────────────────────────────────────┐
│                    📄 MEETING PREPARATION DOCUMENT                     │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  Meeting: Schedule client meeting                                      │
│  Date: March 5, 2026, 10:00 AM - 11:00 AM                             │
│  Generated: February 28, 2026                                          │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │                                                                  │ │
│  │  📋 CONTEXT SUMMARY                                              │ │
│  │  ────────────────────────────────────────────────────────────    │ │
│  │                                                                  │ │
│  │  This meeting is scheduled to discuss Q4 planning with the       │ │
│  │  client. The meeting follows up on the email discussion about    │ │
│  │  action items including budget review and project timeline       │ │
│  │  updates. The client meeting should address project progress,    │ │
│  │  upcoming milestones, and Q4 deliverables.                       │ │
│  │                                                                  │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │                                                                  │ │
│  │  💡 KEY TALKING POINTS                                           │ │
│  │  ────────────────────────────────────────────────────────────    │ │
│  │                                                                  │ │
│  │  1. Q4 Budget Review Status                                      │ │
│  │     • Current budget allocation                                  │ │
│  │     • Proposed changes for Q4                                    │ │
│  │     • Timeline for finalization                                  │ │
│  │                                                                  │ │
│  │  2. Project Timeline Updates                                     │ │
│  │     • Current project status                                     │ │
│  │     • Upcoming milestones                                        │ │
│  │     • Any delays or adjustments needed                           │ │
│  │                                                                  │ │
│  │  3. Client Expectations for Q4                                   │ │
│  │     • Deliverables and deadlines                                 │ │
│  │     • Resource requirements                                      │ │
│  │     • Success metrics                                            │ │
│  │                                                                  │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │                                                                  │ │
│  │  ❓ QUESTIONS TO ASK                                             │ │
│  │  ────────────────────────────────────────────────────────────    │ │
│  │                                                                  │ │
│  │  • What are the client's top priorities for Q4?                  │ │
│  │  • Are there any concerns about the current project timeline?    │ │
│  │  • What is the approval process for the Q4 budget?               │ │
│  │  • Are there any additional resources needed from our side?      │ │
│  │  • What are the key success metrics for this quarter?            │ │
│  │  • When should we schedule the next follow-up meeting?           │ │
│  │                                                                  │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │                                                                  │ │
│  │  ⚠️  POTENTIAL RISKS & CONCERNS                                  │ │
│  │  ────────────────────────────────────────────────────────────    │ │
│  │                                                                  │ │
│  │  • Budget approval deadline is tight (tomorrow EOD)              │ │
│  │  • Project timeline updates may reveal delays                    │ │
│  │  • Client expectations may not align with current capacity       │ │
│  │  • Q4 planning requires coordination across multiple teams       │ │
│  │                                                                  │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │                                                                  │ │
│  │  📎 RELATED TASKS                                                │ │
│  │  ────────────────────────────────────────────────────────────    │ │
│  │                                                                  │ │
│  │  • Review Q4 budget proposal (Due: Tomorrow)                     │ │
│  │  • Update project timeline (Due: Friday)                         │ │
│  │                                                                  │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                        │
│  [Export to PDF]  [Close]                                              │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```


## 6. Deadline Adjustment Modal

```
┌────────────────────────────────────────────────────────────────────────┐
│                                                                        │
│                                                                        │
│         ┌────────────────────────────────────────────────┐            │
│         │                                                │            │
│         │  📅 Adjust Task Deadline                       │            │
│         │                                                │            │
│         ├────────────────────────────────────────────────┤            │
│         │                                                │            │
│         │  Task: Update project timeline                 │            │
│         │                                                │            │
│         │  Current Deadline: Friday, March 1, 2026       │            │
│         │                                                │            │
│         │  ────────────────────────────────────────────  │            │
│         │                                                │            │
│         │  New Deadline:                                 │            │
│         │                                                │            │
│         │  ┌──────────────────────────────────────────┐ │            │
│         │  │  March 1, 2026                    [📅]   │ │            │
│         │  └──────────────────────────────────────────┘ │            │
│         │                                                │            │
│         │  Time (optional):                              │            │
│         │                                                │            │
│         │  ┌──────────────────────────────────────────┐ │            │
│         │  │  5:00 PM                          [🕐]   │ │            │
│         │  └──────────────────────────────────────────┘ │            │
│         │                                                │            │
│         │  ────────────────────────────────────────────  │            │
│         │                                                │            │
│         │  ⚠️  Note: Changing the deadline will trigger  │            │
│         │     calendar rescheduling if a block exists.  │            │
│         │                                                │            │
│         │  ────────────────────────────────────────────  │            │
│         │                                                │            │
│         │         [Cancel]        [Save Changes]         │            │
│         │                                                │            │
│         └────────────────────────────────────────────────┘            │
│                                                                        │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```


## 7. Scheduling Conflict View

```
┌────────────────────────────────────────────────────────────────────────┐
│                           📋 TASK BOARD                                │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │ 🔴 TODAY                                                         │ │
│  ├──────────────────────────────────────────────────────────────────┤ │
│  │                                                                  │ │
│  │  ┌────────────────────────────────────────────────────────────┐ │ │
│  │  │ 🔴 HIGH PRIORITY                    Confidence: 92% ✓      │ │ │
│  │  │                                                            │ │ │
│  │  │ Prepare presentation for board meeting                     │ │ │
│  │  │                                                            │ │ │
│  │  │ 📝 Create and finalize presentation slides for the         │ │ │
│  │  │    quarterly board meeting                                 │ │ │
│  │  │                                                            │ │ │
│  │  │ 📅 Deadline: Today, 5:00 PM                                │ │ │
│  │  │ 👤 Owner: You                                              │ │ │
│  │  │                                                            │ │ │
│  │  │ ⚠️  STATUS: SCHEDULING CONFLICT                            │ │ │
│  │  │                                                            │ │ │
│  │  │ ┌────────────────────────────────────────────────────────┐ │ │ │
│  │  │ │ ⚠️  Unable to schedule calendar block                  │ │ │ │
│  │  │ │                                                        │ │ │ │
│  │  │ │ Reason: No available time slots before deadline        │ │ │ │
│  │  │ │                                                        │ │ │ │
│  │  │ │ Conflicting events:                                    │ │ │ │
│  │  │ │ • 2:00 PM - 3:00 PM: Team standup                      │ │ │ │
│  │  │ │ • 3:30 PM - 4:30 PM: Client call                       │ │ │ │
│  │  │ │ • 4:30 PM - 5:00 PM: 1-on-1 with manager               │ │ │ │
│  │  │ │                                                        │ │ │ │
│  │  │ │ Suggestions:                                           │ │ │ │
│  │  │ │ • Extend deadline to tomorrow                          │ │ │ │
│  │  │ │ • Manually schedule during lunch break                 │ │ │ │
│  │  │ │ • Reschedule one of the conflicting events             │ │ │ │
│  │  │ └────────────────────────────────────────────────────────┘ │ │ │
│  │  │                                                            │ │ │
│  │  │ 💬 Source: "Prepare presentation for board meeting by      │ │ │
│  │  │            today 5pm"                                      │ │ │
│  │  │                                                            │ │ │
│  │  │ [Adjust Deadline]  [Manual Schedule]  [Discard Task]      │ │ │
│  │  └────────────────────────────────────────────────────────────┘ │ │
│  │                                                                  │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```


## 8. Export Options Menu

```
┌────────────────────────────────────────────────────────────────────────┐
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │ ✅ Agent Execution Complete                                      │ │
│  │                                                                  │ │
│  │                                    ┌───────────────────────────┐ │ │
│  │                                    │  📤 Export Options        │ │ │
│  │                                    ├───────────────────────────┤ │ │
│  │                                    │                           │ │ │
│  │                                    │  📊 Export Tasks to CSV   │ │ │
│  │                                    │                           │ │ │
│  │                                    │  📄 Export Meeting Prep   │ │ │
│  │                                    │     Documents to PDF      │ │ │
│  │                                    │                           │ │ │
│  │                                    │  📋 Export Execution      │ │ │
│  │                                    │     Logs to TXT           │ │ │
│  │                                    │                           │ │ │
│  │                                    │  📦 Export All (ZIP)      │ │ │
│  │                                    │                           │ │ │
│  │                                    └───────────────────────────┘ │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

## 9. CSV Export Preview

```
┌────────────────────────────────────────────────────────────────────────┐
│                        📊 CSV EXPORT PREVIEW                           │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  File: ai_execution_agent_tasks_2026-02-28.csv                        │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │                                                                  │ │
│  │  Title,Description,Deadline,Owner,Priority,Confidence,State,...  │ │
│  │  "Review Q4 budget proposal","Review and finalize the Q4...     │ │
│  │  "Schedule client meeting","Arrange and schedule a meeting...   │ │
│  │  "Update project timeline","Update and revise the project...    │ │
│  │                                                                  │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                        │
│  Preview shows first 3 rows. Full export contains:                    │
│  • 3 tasks                                                             │
│  • 10 columns (Title, Description, Deadline, Owner, Priority,         │
│    Confidence, State, Calendar Block ID, Source Snippet, Created)     │
│                                                                        │
│  [Download CSV]  [Cancel]                                              │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```


## 10. Error State View

```
┌────────────────────────────────────────────────────────────────────────┐
│ Gmail                                                    [User Profile] │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │ ← Back to Inbox                                                  │ │
│  ├──────────────────────────────────────────────────────────────────┤ │
│  │                                                                  │ │
│  │  From: john.doe@company.com                                      │ │
│  │  Subject: Q4 Planning - Action Items                             │ │
│  │                                                                  │ │
│  │  ┌────────────────────────────────────────────────────────────┐ │ │
│  │  │  ❌ Agent Execution Failed                                 │ │ │
│  │  │                                                            │ │ │
│  │  │  ┌──────────────────────────────────────────────────────┐ │ │ │
│  │  │  │  ⚠️  Error: LLM API Request Failed                    │ │ │ │
│  │  │  │                                                      │ │ │ │
│  │  │  │  Unable to connect to OpenAI API. This may be due   │ │ │ │
│  │  │  │  to:                                                 │ │ │ │
│  │  │  │                                                      │ │ │ │
│  │  │  │  • Invalid API key                                   │ │ │ │
│  │  │  │  • API quota exceeded                                │ │ │ │
│  │  │  │  • Network connectivity issues                       │ │ │ │
│  │  │  │  • Service temporarily unavailable                   │ │ │ │
│  │  │  │                                                      │ │ │ │
│  │  │  │  Suggested Actions:                                  │ │ │ │
│  │  │  │  1. Check your API key configuration                 │ │ │ │
│  │  │  │  2. Verify your API quota/credits                    │ │ │ │
│  │  │  │  3. Check network connection                         │ │ │ │
│  │  │  │  4. Try again in a few moments                       │ │ │ │
│  │  │  │                                                      │ │ │ │
│  │  │  │  Error Code: 401 Unauthorized                        │ │ │ │
│  │  │  │  Timestamp: 2026-02-28 10:45:34                      │ │ │ │
│  │  │  │                                                      │ │ │ │
│  │  │  └──────────────────────────────────────────────────────┘ │ │ │
│  │  │                                                            │ │ │
│  │  │  [View Logs]  [Retry]  [Close]                            │ │ │
│  │  └────────────────────────────────────────────────────────────┘ │ │
│  │                                                                  │ │
│  │  ──────────────────────────────────────────────────────────────  │ │
│  │                                                                  │ │
│  │  [Email content continues below...]                              │ │
│  │                                                                  │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```


## 11. Mobile Responsive View (Future Enhancement)

```
┌─────────────────────┐
│  Gmail Mobile       │
│                 [≡] │
├─────────────────────┤
│                     │
│  From: john.doe@... │
│  Subject: Q4 Plan...│
│                     │
│  ┌─────────────────┐│
│  │ 🤖 Run Agent    ││
│  └─────────────────┘│
│                     │
│  ─────────────────  │
│                     │
│  Hi Team,           │
│                     │
│  Following up on... │
│                     │
│  1. Review the Q4...│
│  2. Schedule a...   │
│  3. Update proj...  │
│                     │
│  [Read More]        │
│                     │
└─────────────────────┘


After Processing:

┌─────────────────────┐
│  AI Agent Results   │
│                 [×] │
├─────────────────────┤
│                     │
│  📊 Summary         │
│  ┌─────────────────┐│
│  │ Tasks: 3        ││
│  │ Scheduled: 2    ││
│  │ Review: 1       ││
│  └─────────────────┘│
│                     │
│  🔴 TODAY           │
│  ┌─────────────────┐│
│  │ 🔴 HIGH         ││
│  │ Review Q4 bud...││
│  │ ✅ Scheduled    ││
│  │ [Details ▼]     ││
│  └─────────────────┘│
│                     │
│  🟢 UPCOMING        │
│  ┌─────────────────┐│
│  │ 🟡 MEDIUM       ││
│  │ Schedule cli... ││
│  │ ✅ Scheduled    ││
│  │ 📄 Prep Doc     ││
│  │ [Details ▼]     ││
│  └─────────────────┘│
│                     │
│  ┌─────────────────┐│
│  │ 🟡 MEDIUM       ││
│  │ Update proj...  ││
│  │ ⚠️ Review       ││
│  │ [Details ▼]     ││
│  └─────────────────┘│
│                     │
│  [Export] [Close]   │
│                     │
└─────────────────────┘
```


## 12. System Architecture Visualization

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        SYSTEM ARCHITECTURE                              │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                          PRESENTATION LAYER                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                      Gmail Web Interface                         │  │
│  │                                                                  │  │
│  │  ┌────────────────────────────────────────────────────────────┐ │  │
│  │  │         Chrome Extension (Content Script)                  │ │  │
│  │  │                                                            │ │  │
│  │  │  • DOM Extraction                                          │ │  │
│  │  │  • Button Injection                                        │ │  │
│  │  │  • Task Board Rendering                                    │ │  │
│  │  │  • Feedback Panel Display                                  │ │  │
│  │  └────────────────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTPS POST /run-agent
                                    │ (JSON Payload)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          APPLICATION LAYER                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                      FastAPI Backend                             │  │
│  │                                                                  │  │
│  │  ┌────────────────────────────────────────────────────────────┐ │  │
│  │  │  API Layer                                                 │ │  │
│  │  │  • Request Validation (Pydantic)                           │ │  │
│  │  │  • CORS Configuration                                      │ │  │
│  │  │  • Error Handling                                          │ │  │
│  │  └────────────────────────────────────────────────────────────┘ │  │
│  │                                                                  │  │
│  │  ┌────────────────────────────────────────────────────────────┐ │  │
│  │  │  Task Extraction Service                                   │ │  │
│  │  │  • LLM API Integration                                     │ │  │
│  │  │  • JSON Parsing                                            │ │  │
│  │  │  • Confidence Scoring                                      │ │  │
│  │  └────────────────────────────────────────────────────────────┘ │  │
│  │                                                                  │  │
│  │  ┌────────────────────────────────────────────────────────────┐ │  │
│  │  │  Post-Processing Service                                   │ │  │
│  │  │  • Priority Assignment (Rule-Based)                        │ │  │
│  │  │  • Deadline Resolution                                     │ │  │
│  │  │  • Task Validation                                         │ │  │
│  │  └────────────────────────────────────────────────────────────┘ │  │
│  │                                                                  │  │
│  │  ┌────────────────────────────────────────────────────────────┐ │  │
│  │  │  Calendar Service                                          │ │  │
│  │  │  • Slot Finding Algorithm                                  │ │  │
│  │  │  • Conflict Detection                                      │ │  │
│  │  │  • Block Creation                                          │ │  │
│  │  └────────────────────────────────────────────────────────────┘ │  │
│  │                                                                  │  │
│  │  ┌────────────────────────────────────────────────────────────┐ │  │
│  │  │  Meeting Prep Service                                      │ │  │
│  │  │  • Meeting Detection                                       │ │  │
│  │  │  • Document Generation                                     │ │  │
│  │  │  • Context Extraction                                      │ │  │
│  │  └────────────────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                    │                              │
                    │                              │
                    ▼                              ▼
┌─────────────────────────────────┐  ┌─────────────────────────────────┐
│     EXTERNAL SERVICES           │  │     EXTERNAL SERVICES           │
├─────────────────────────────────┤  ├─────────────────────────────────┤
│                                 │  │                                 │
│  ┌───────────────────────────┐ │  │  ┌───────────────────────────┐ │
│  │  OpenAI / Gemini API      │ │  │  │  Google Calendar API      │ │
│  │                           │ │  │  │                           │ │
│  │  • GPT-4 / GPT-3.5        │ │  │  │  • Event Retrieval        │ │
│  │  • Gemini Pro             │ │  │  │  • Event Creation         │ │
│  │  • Structured Output      │ │  │  │  • OAuth2 Auth            │ │
│  └───────────────────────────┘ │  │  └───────────────────────────┘ │
│                                 │  │                                 │
└─────────────────────────────────┘  └─────────────────────────────────┘
```


## 13. User Journey Map

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          USER JOURNEY MAP                               │
└─────────────────────────────────────────────────────────────────────────┘

PHASE 1: DISCOVERY
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  User Action:    Opens email with action items                         │
│  Touchpoint:     Gmail inbox                                           │
│  Emotion:        😐 Neutral - Reading email                            │
│  Pain Point:     "I need to manually track all these tasks"            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
PHASE 2: ACTIVATION
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  User Action:    Notices "Run Agent" button                            │
│  Touchpoint:     Chrome Extension UI                                   │
│  Emotion:        🤔 Curious - "What does this do?"                     │
│  Opportunity:    Clear value proposition needed                        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
PHASE 3: PROCESSING
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  User Action:    Clicks "Run Agent"                                    │
│  Touchpoint:     Loading state with progress                           │
│  Emotion:        ⏳ Waiting - "Is this working?"                       │
│  Need:           Clear progress indication                             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
PHASE 4: REVIEW
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  User Action:    Reviews extracted tasks                               │
│  Touchpoint:     Task Board UI                                         │
│  Emotion:        😊 Pleased - "This saved me time!"                    │
│  Value:          Tasks organized, priorities assigned                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
PHASE 5: ADJUSTMENT
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  User Action:    Adjusts deadlines, reviews low-confidence tasks       │
│  Touchpoint:     Task management actions                               │
│  Emotion:        😌 Confident - "I'm in control"                       │
│  Value:          Transparency and user control                         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
PHASE 6: COMPLETION
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  User Action:    Checks calendar, exports data                         │
│  Touchpoint:     Google Calendar, Export features                      │
│  Emotion:        😄 Satisfied - "My calendar is organized!"            │
│  Outcome:        30-60 minutes saved, reduced stress                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```


## 14. Color Scheme & Design System

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        DESIGN SYSTEM GUIDE                              │
└─────────────────────────────────────────────────────────────────────────┘

COLOR PALETTE
─────────────────────────────────────────────────────────────────────────

Primary Colors:
  🔵 Primary Blue:     #4285F4  (Buttons, Links)
  🟢 Success Green:    #34A853  (Scheduled tasks, Success states)
  🔴 High Priority:    #EA4335  (Urgent tasks, Errors)
  🟡 Warning Yellow:   #FBBC04  (Medium priority, Warnings)

Secondary Colors:
  ⚪ Background:       #FFFFFF  (Main background)
  ⬜ Light Gray:       #F8F9FA  (Card backgrounds)
  ⬛ Dark Gray:        #5F6368  (Text, Icons)
  🔘 Border Gray:      #DADCE0  (Borders, Dividers)

Status Colors:
  ✅ Scheduled:        #34A853  (Green)
  ⚠️  Manual Review:   #FBBC04  (Yellow)
  ❌ Conflict:         #EA4335  (Red)
  ℹ️  Info:            #4285F4  (Blue)


TYPOGRAPHY
─────────────────────────────────────────────────────────────────────────

Headings:
  H1: 24px, Bold, #202124
  H2: 20px, Bold, #202124
  H3: 16px, Bold, #5F6368

Body Text:
  Regular: 14px, Normal, #5F6368
  Small:   12px, Normal, #80868B

Labels:
  Badge:   12px, Bold, Uppercase


SPACING
─────────────────────────────────────────────────────────────────────────

  XS:  4px   (Icon padding)
  S:   8px   (Element spacing)
  M:   16px  (Card padding)
  L:   24px  (Section spacing)
  XL:  32px  (Major section spacing)


COMPONENTS
─────────────────────────────────────────────────────────────────────────

Button:
  ┌─────────────────┐
  │  🤖 Run Agent   │  Primary: #4285F4, White text, 8px radius
  └─────────────────┘

  ┌─────────────────┐
  │  Adjust Deadline│  Secondary: White, #4285F4 text, 1px border
  └─────────────────┘

Task Card:
  ┌─────────────────────────────────────┐
  │ 🔴 HIGH PRIORITY    Confidence: 95% │  Border-left: 4px solid (priority color)
  │                                     │  Background: #FFFFFF
  │ Task Title                          │  Padding: 16px
  │ Description text...                 │  Border-radius: 8px
  │                                     │  Box-shadow: 0 1px 3px rgba(0,0,0,0.1)
  │ [Actions]                           │
  └─────────────────────────────────────┘

Badge:
  ┌──────────┐
  │ HIGH     │  Background: #EA4335, White text, 4px radius
  └──────────┘

  ┌──────────┐
  │ MEDIUM   │  Background: #FBBC04, White text, 4px radius
  └──────────┘

  ┌──────────┐
  │ LOW      │  Background: #34A853, White text, 4px radius
  └──────────┘


ICONS
─────────────────────────────────────────────────────────────────────────

  🤖  Agent/AI
  📋  Tasks/List
  📅  Calendar/Date
  👤  User/Owner
  ✅  Success/Scheduled
  ⚠️   Warning/Review
  ❌  Error/Conflict
  📝  Description/Notes
  💬  Source/Quote
  📊  Statistics/Analytics
  ⏱️   Time/Duration
  🔴  High Priority
  🟡  Medium Priority
  🟢  Low Priority
  📄  Document/PDF
  📤  Export
  🔍  Review/Inspect
```


## 15. Interaction States

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        BUTTON INTERACTION STATES                        │
└─────────────────────────────────────────────────────────────────────────┘

DEFAULT STATE
┌─────────────────┐
│  🤖 Run Agent   │  Background: #4285F4, Cursor: pointer
└─────────────────┘

HOVER STATE
┌─────────────────┐
│  🤖 Run Agent   │  Background: #3367D6 (darker), Cursor: pointer
└─────────────────┘

ACTIVE/PRESSED STATE
┌─────────────────┐
│  🤖 Run Agent   │  Background: #2851A3 (darkest), Scale: 0.98
└─────────────────┘

DISABLED STATE
┌─────────────────┐
│  🤖 Run Agent   │  Background: #DADCE0, Cursor: not-allowed, Opacity: 0.6
└─────────────────┘

LOADING STATE
┌─────────────────┐
│  ⏳ Processing  │  Background: #4285F4, Spinner animation
└─────────────────┘


┌─────────────────────────────────────────────────────────────────────────┐
│                        TASK CARD INTERACTION STATES                     │
└─────────────────────────────────────────────────────────────────────────┘

DEFAULT STATE
┌─────────────────────────────────────────┐
│ 🔴 HIGH PRIORITY    Confidence: 95%     │  Box-shadow: 0 1px 3px rgba(0,0,0,0.1)
│                                         │
│ Task Title                              │
│ Description...                          │
└─────────────────────────────────────────┘

HOVER STATE
┌─────────────────────────────────────────┐
│ 🔴 HIGH PRIORITY    Confidence: 95%     │  Box-shadow: 0 4px 8px rgba(0,0,0,0.15)
│                                         │  Transform: translateY(-2px)
│ Task Title                              │  Cursor: pointer
│ Description...                          │
└─────────────────────────────────────────┘

EXPANDED STATE
┌─────────────────────────────────────────┐
│ 🔴 HIGH PRIORITY    Confidence: 95% ▲   │  Full details visible
│                                         │  Actions visible
│ Task Title                              │
│ Description...                          │
│ [Full details shown]                    │
│ [Adjust] [Discard] [View Calendar]     │
└─────────────────────────────────────────┘

COLLAPSED STATE
┌─────────────────────────────────────────┐
│ 🔴 HIGH PRIORITY    Confidence: 95% ▼   │  Minimal details
│ Task Title                              │  Click to expand
└─────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────┐
│                        FEEDBACK STATES                                  │
└─────────────────────────────────────────────────────────────────────────┘

SUCCESS MESSAGE
┌─────────────────────────────────────────┐
│ ✅ Agent Execution Complete             │  Background: #E6F4EA (light green)
│                                         │  Border-left: 4px solid #34A853
│ 3 tasks extracted and scheduled         │  Auto-dismiss after 5 seconds
└─────────────────────────────────────────┘

ERROR MESSAGE
┌─────────────────────────────────────────┐
│ ❌ Agent Execution Failed               │  Background: #FCE8E6 (light red)
│                                         │  Border-left: 4px solid #EA4335
│ Unable to connect to LLM API            │  Manual dismiss required
│ [View Details] [Retry]                  │
└─────────────────────────────────────────┘

WARNING MESSAGE
┌─────────────────────────────────────────┐
│ ⚠️  Low Confidence Task Detected        │  Background: #FEF7E0 (light yellow)
│                                         │  Border-left: 4px solid #FBBC04
│ Please review task details manually     │  Auto-dismiss after 8 seconds
└─────────────────────────────────────────┘

INFO MESSAGE
┌─────────────────────────────────────────┐
│ ℹ️  Processing Email Content            │  Background: #E8F0FE (light blue)
│                                         │  Border-left: 4px solid #4285F4
│ This may take 10-15 seconds             │  Auto-dismiss on completion
└─────────────────────────────────────────┘
```


## 16. Responsive Breakpoints

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        RESPONSIVE DESIGN BREAKPOINTS                    │
└─────────────────────────────────────────────────────────────────────────┘

DESKTOP (> 1024px)
┌───────────────────────────────────────────────────────────────────────┐
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │  Task Board (Full Width)                                        │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │ │
│  │  │   TODAY      │  │  TOMORROW    │  │  UPCOMING    │         │ │
│  │  │              │  │              │  │              │         │ │
│  │  │  [Tasks...]  │  │  [Tasks...]  │  │  [Tasks...]  │         │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘         │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │  Feedback Panel (Side by Side)                                  │ │
│  │  ┌──────────────────┐  ┌──────────────────────────────────────┐│ │
│  │  │  Statistics      │  │  Execution Logs                      ││ │
│  │  └──────────────────┘  └──────────────────────────────────────┘│ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘


TABLET (768px - 1024px)
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │  Task Board (Stacked)                             │ │
│  │  ┌─────────────────────────────────────────────┐ │ │
│  │  │   TODAY                                     │ │ │
│  │  │   [Tasks...]                                │ │ │
│  │  └─────────────────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────────────────┐ │ │
│  │  │   TOMORROW                                  │ │ │
│  │  │   [Tasks...]                                │ │ │
│  │  └─────────────────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────────────────┐ │ │
│  │  │   UPCOMING                                  │ │ │
│  │  │   [Tasks...]                                │ │ │
│  │  └─────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │  Feedback Panel (Stacked)                         │ │
│  │  ┌─────────────────────────────────────────────┐ │ │
│  │  │  Statistics                                 │ │ │
│  │  └─────────────────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────────────────┐ │ │
│  │  │  Execution Logs                             │ │ │
│  │  └─────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
└─────────────────────────────────────────────────────────┘


MOBILE (< 768px)
┌─────────────────────────┐
│                         │
│  ┌───────────────────┐  │
│  │  Task Board       │  │
│  │  (Accordion)      │  │
│  │                   │  │
│  │  🔴 TODAY ▼       │  │
│  │  ┌─────────────┐ │  │
│  │  │ Task 1      │ │  │
│  │  │ [Details ▼] │ │  │
│  │  └─────────────┘ │  │
│  │                   │  │
│  │  🟡 TOMORROW ▶    │  │
│  │  (Collapsed)      │  │
│  │                   │  │
│  │  🟢 UPCOMING ▶    │  │
│  │  (Collapsed)      │  │
│  └───────────────────┘  │
│                         │
│  ┌───────────────────┐  │
│  │  📊 Stats         │  │
│  │  Tasks: 3         │  │
│  │  Scheduled: 2     │  │
│  │  [View Logs]      │  │
│  └───────────────────┘  │
│                         │
│  [Export ▼]             │
│                         │
└─────────────────────────┘
```


## 17. Accessibility Features

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        ACCESSIBILITY CONSIDERATIONS                     │
└─────────────────────────────────────────────────────────────────────────┘

KEYBOARD NAVIGATION
─────────────────────────────────────────────────────────────────────────

Tab Order:
  1. "Run Agent" button
  2. Task cards (in order: Today → Tomorrow → Upcoming)
  3. Action buttons within each task
  4. Export button
  5. Feedback panel elements

Keyboard Shortcuts:
  • Enter/Space:  Activate focused button
  • Tab:          Move to next element
  • Shift+Tab:    Move to previous element
  • Escape:       Close modals/dialogs
  • Arrow Keys:   Navigate within task lists


SCREEN READER SUPPORT
─────────────────────────────────────────────────────────────────────────

ARIA Labels:
  <button aria-label="Run AI Agent to extract tasks from email">
    🤖 Run Agent
  </button>

  <div role="region" aria-label="Task Board">
    <section aria-label="Today's tasks">
      <article aria-label="High priority task: Review Q4 budget proposal">
        ...
      </article>
    </section>
  </div>

Live Regions:
  <div aria-live="polite" aria-atomic="true">
    ✅ Agent execution complete. 3 tasks extracted.
  </div>

  <div aria-live="assertive" aria-atomic="true">
    ❌ Error: Unable to connect to API
  </div>


VISUAL ACCESSIBILITY
─────────────────────────────────────────────────────────────────────────

Color Contrast:
  • Text on background: 4.5:1 minimum (WCAG AA)
  • Large text: 3:1 minimum
  • Interactive elements: 3:1 minimum

Focus Indicators:
  ┌─────────────────┐
  │  🤖 Run Agent   │  2px solid #4285F4 outline
  └─────────────────┘  4px offset

Text Sizing:
  • Minimum: 14px (body text)
  • Scalable: Supports browser zoom up to 200%
  • Relative units: rem/em instead of px


MOTION & ANIMATION
─────────────────────────────────────────────────────────────────────────

Reduced Motion Support:
  @media (prefers-reduced-motion: reduce) {
    * {
      animation-duration: 0.01ms !important;
      transition-duration: 0.01ms !important;
    }
  }

Loading Indicators:
  • Spinner with aria-label="Loading"
  • Progress bar with aria-valuenow, aria-valuemin, aria-valuemax
  • Text alternative: "Processing email content..."


ERROR HANDLING
─────────────────────────────────────────────────────────────────────────

Error Messages:
  <div role="alert" aria-live="assertive">
    ❌ Error: Unable to connect to LLM API
    <p>Suggested actions:</p>
    <ul>
      <li>Check your API key configuration</li>
      <li>Verify network connection</li>
      <li><button>Retry</button></li>
    </ul>
  </div>

Form Validation:
  <label for="deadline-input">New Deadline</label>
  <input 
    id="deadline-input"
    type="date"
    aria-required="true"
    aria-invalid="false"
    aria-describedby="deadline-error"
  />
  <span id="deadline-error" role="alert"></span>
```

## Summary

This wireframe document provides:

1. **Gmail Integration Views** - How the extension appears in Gmail
2. **Task Board Interface** - Main interaction point with extracted tasks
3. **Feedback & Logging** - Transparency and execution details
4. **Meeting Prep Documents** - Generated preparation materials
5. **Interactive Modals** - Deadline adjustment, export options
6. **Error States** - Clear error handling and recovery
7. **Mobile Views** - Responsive design considerations
8. **System Architecture** - Visual component relationships
9. **User Journey** - Complete user experience flow
10. **Design System** - Colors, typography, spacing, components
11. **Interaction States** - Button, card, and feedback states
12. **Responsive Breakpoints** - Desktop, tablet, mobile layouts
13. **Accessibility** - Keyboard navigation, screen readers, WCAG compliance

These wireframes demonstrate a clean, user-friendly interface that prioritizes transparency, user control, and accessibility while maintaining the deterministic AI orchestration philosophy of the system.

