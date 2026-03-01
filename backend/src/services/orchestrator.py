"""Orchestration layer for coordinating all services."""

from typing import List, Dict, Any
from datetime import datetime

from models.models import (
    RunAgentRequestModel,
    RunAgentResponseModel,
    FeedbackStatsModel,
    LogEntryModel,
    ErrorDetailModel,
    TaskModel,
    MeetingPrepDocument
)
from src.services.extraction import TaskExtractionService, ExtractionError
from src.services.post_processing import PostProcessingService
from src.services.calendar import CalendarService
from src.services.meeting_prep import MeetingPrepService


class AgentOrchestrator:
    """Orchestrator for coordinating all agent services."""

    CONFIDENCE_THRESHOLD = 0.7

    def __init__(
        self,
        extraction_service: TaskExtractionService,
        post_processing_service: PostProcessingService,
        calendar_service: CalendarService,
        meeting_prep_service: MeetingPrepService
    ):
        self.extraction = extraction_service
        self.post_processing = post_processing_service
        self.calendar = calendar_service
        self.meeting_prep = meeting_prep_service

    def run_agent(self, request: RunAgentRequestModel) -> RunAgentResponseModel:
        """
        Orchestrate the full agent execution flow.
        """
        logs: List[LogEntryModel] = []
        errors: List[ErrorDetailModel] = []
        stats = FeedbackStatsModel(
            tasks_extracted=0,
            calendar_blocks_created=0,
            scheduling_conflicts=0,
            manual_review_items=0
        )

        try:
            # Step 1: Extract tasks
            logs.append(LogEntryModel(timestamp=datetime.now(), message="Extracting tasks from email"))
            raw_tasks = self.extraction.extract_tasks(request.email_content)
            stats.tasks_extracted = len(raw_tasks)

            # Step 2: Post-process tasks
            logs.append(LogEntryModel(timestamp=datetime.now(), message="Post-processing tasks"))
            processed_tasks = self.post_processing.process_tasks(raw_tasks, datetime.now())

            # Step 3: Schedule tasks and generate prep docs
            final_tasks: List[TaskModel] = []
            for task in processed_tasks:
                # Check confidence threshold
                if task['confidence'] < self.CONFIDENCE_THRESHOLD:
                    task['state'] = 'manual_review'
                    stats.manual_review_items += 1
                    logs.append(LogEntryModel(
                        timestamp=datetime.now(),
                        message=f"Task '{task['title']}' marked for manual review (confidence: {task['confidence']})"
                    ))
                else:
                    # Try to schedule
                    try:
                        block_id, error = self.calendar.find_slot_and_create_block(
                            task,
                            request.calendar_id,
                            request.user_timezone
                        )

                        if error == "scheduling_conflict":
                            task['state'] = 'scheduling_conflict'
                            stats.scheduling_conflicts += 1
                            logs.append(LogEntryModel(
                                timestamp=datetime.now(),
                                message=f"Scheduling conflict for task '{task['title']}'"
                            ))
                        else:
                            task['calendar_block_id'] = block_id
                            task['state'] = 'scheduled'
                            stats.calendar_blocks_created += 1
                            print(f"✓ CREATED CALENDAR BLOCK: {task['title']} - ID: {block_id}")
                            logs.append(LogEntryModel(
                                timestamp=datetime.now(),
                                message=f"Created calendar block for task '{task['title']}'"
                            ))
                    except Exception as e:
                        print(f"✗ CALENDAR ERROR for '{task['title']}': {e}")
                        import traceback
                        traceback.print_exc()
                        task['state'] = 'error'
                        errors.append(ErrorDetailModel(
                            code="CALENDAR_ERROR",
                            message=str(e)
                        ))

                    # Generate meeting prep if applicable
                    prep_doc = self.meeting_prep.detect_and_generate_prep(
                        task,
                        request.email_content
                    )
                    if prep_doc:
                        task['meeting_prep'] = prep_doc
                        logs.append(LogEntryModel(
                            timestamp=datetime.now(),
                            message=f"Generated meeting prep for '{task['title']}'"
                        ))

                final_tasks.append(TaskModel(**task))

            return RunAgentResponseModel(
                tasks=final_tasks,
                stats=stats,
                logs=logs,
                errors=errors
            )

        except ExtractionError as e:
            errors.append(ErrorDetailModel(
                code="EXTRACTION_ERROR",
                message=str(e),
                context={"step": "extraction"}
            ))
            return RunAgentResponseModel(
                tasks=[],
                stats=stats,
                logs=logs,
                errors=errors
            )
        except Exception as e:
            errors.append(ErrorDetailModel(
                code="AGENT_EXECUTION_ERROR",
                message=str(e),
                context={"step": "orchestration"}
            ))
            return RunAgentResponseModel(
                tasks=[],
                stats=stats,
                logs=logs,
                errors=errors
            )
