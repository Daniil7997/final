from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.domain.meetings.exceptions import (
    InvalidMeetingTimeRangeError,
    MeetingNotFoundError,
    MeetingsOverlapError,
    UserAlreadyInMeetingError,
)


def register_meetings_errors_handlers(app: FastAPI) -> None:

    @app.exception_handler(MeetingsOverlapError)
    async def handle_meeting_overlap(
        request: Request,
        exc: MeetingsOverlapError
    ) -> JSONResponse:
        text = ("A meeting is already scheduled for this time.")
        msg = exc.msg or text
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"msg": msg}
        )

    @app.exception_handler(InvalidMeetingTimeRangeError)
    async def handle_invalid_meeting_time_range(
        request: Request,
        exc: InvalidMeetingTimeRangeError
    ) -> JSONResponse:
        text = ("End time cannot be earlier than start time.")
        msg = exc.msg or text
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"msg": msg}
        )

    @app.exception_handler(MeetingNotFoundError)
    async def handle_meeting_not_found(
        request: Request,
        exc: MeetingNotFoundError
    ) -> JSONResponse:
        msg = exc.msg or "Meeting not found"
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": msg}
        )

    @app.exception_handler(UserAlreadyInMeetingError)
    async def handle_user_already_in_meeting(
        request: Request,
        exc: UserAlreadyInMeetingError
    ) -> JSONResponse:
        msg = exc.msg or "The user is already in this meeting."
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"msg": msg}
        )
