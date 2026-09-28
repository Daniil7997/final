import typing
import datetime as dt

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import (select,
                        Select,
                        Update,
                        Delete)
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import insert

from app.models.users import Users, UsersRoles
from app.models.teams import Teams, TeamMembership
from app.models.tasks import Tasks, TasksComments
from app.models.evaluations import Evaluations
from app.models.meetings import Meetings, MeetingsParticipants

from app.schemas.types import IdType


T_Stmt = typing.TypeVar("T_Stmt", Select, Update, Delete)


class BaseFactory:
    def __init__(self, session: AsyncSession):
        self.session = session


class UsersFactory(BaseFactory):

    async def create_user(self,
                          name: str,
                          email: str,
                          hashed_password: str,
                          role: UsersRoles = UsersRoles.member) -> Users:
        user = Users(name=name,
                     email=email,
                     password=hashed_password,
                     user_role=role)
        self.session.add(user)
        await self.session.flush()
        self.session.expunge(user)
        return user


class TeamsFactory(BaseFactory):

    async def create_team(self,
                          name: str,
                          creator_id: IdType,
                          description: str | None = None) -> Teams:
        team = Teams(name=name, description=description)
        self.session.add(team)
        await self.session.flush()
        membership = TeamMembership(user_id=creator_id,
                                    team_id=team.id,
                                    team_role='creator')
        self.session.add(membership)
        await self.session.flush()
        self.session.expunge(team)
        return team

    async def join_team(self, team_id: IdType, user_id: IdType) -> None:
        stmt = (insert(TeamMembership)
                .values(team_id=team_id, user_id=user_id, team_role='intern')
                .on_conflict_do_nothing())
        await self.session.execute(stmt)
        await self.session.flush()


class TasksFactory(BaseFactory):

    async def create_task(self,
                          description: str,
                          due_date: dt.date,
                          creator_id: IdType,
                          team_id: IdType) -> Tasks:
        task = Tasks(description=description,
                     creator_id=creator_id,
                     team_id=team_id,
                     due_date=due_date)
        self.session.add(task)
        await self.session.flush()
        self.session.expunge(task)
        return task

    async def create_commment(self,
                              task_id: IdType,
                              actor_id: IdType,
                              comment_text: str
                              ) -> None:
        comment_obj = TasksComments(
            task_id=task_id,
            author_id=actor_id,
            comment=comment_text
        )
        self.session.add(comment_obj)


class EvaluationsFactory(BaseFactory):

    async def create_evaluation(self,
                                task_id: IdType,
                                grade: int,
                                grader_id: IdType,
                                author_id: IdType,
                                comment: str | None = None) -> None:
        evaluation = Evaluations(
            task_id=task_id,
            grade=grade,
            grader_id=grader_id,
            author_id=author_id,
            comment=comment
        )
        self.session.add(evaluation)

    async def average_evaluations(self, user_id: IdType) -> float | None:
        stmt = (select(func.avg(Evaluations.grade))
                .where(Evaluations.author_id == user_id))

        result = await self.session.execute(stmt)
        avg_evaluation = result.scalar_one_or_none()
        if avg_evaluation is None:
            return None
        return avg_evaluation


class MeetingsFactory(BaseFactory):

    async def create_meeting(self,
                             team_id: IdType,
                             description: str,
                             start_meeting: dt.datetime,
                             end_meeting: dt.datetime) -> Meetings:
        meeting_obj = Meetings(description=description,
                               start_meeting=start_meeting,
                               end_meeting=end_meeting,
                               team_id=team_id)
        self.session.add(meeting_obj)
        await self.session.flush()
        self.session.expunge(meeting_obj)
        return meeting_obj

    async def join_meeting(self,
                           user_id: IdType,
                           meeting_id: IdType) -> None:
        user_in_meeting = MeetingsParticipants(
            user_id=user_id,
            meeting_id=meeting_id
        )
        self.session.add(user_in_meeting)


class AggregateFactory:
    users: UsersFactory
    teams: TeamsFactory
    tasks: TasksFactory
    meetings: MeetingsFactory
    evaluations: EvaluationsFactory

    def __init__(self, session: AsyncSession):
        self.session = session
        self.users = UsersFactory(session)
        self.teams = TeamsFactory(session)
        self.tasks = TasksFactory(session)
        self.meetings = MeetingsFactory(session)
        self.evaluations = EvaluationsFactory(session)
