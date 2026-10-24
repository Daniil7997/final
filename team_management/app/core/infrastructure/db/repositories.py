import typing
import datetime as dt

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import (exists,
                        select,
                        update,
                        delete,
                        text,
                        Select,
                        Update,
                        Delete,
                        Exists)
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import insert

from app.core.infrastructure.db.models.users import Users
from app.core.infrastructure.db.models.teams import Teams, TeamMembership, TeamsRoles
from app.core.infrastructure.db.models.tasks import Tasks, TasksComments, TaskStatus
from app.core.infrastructure.db.models.evaluations import Evaluations
from app.core.infrastructure.db.models.meetings import Meetings, MeetingsParticipants

from app.schemas.structural import (UsersSchema,
                                    TeamsSchema,
                                    TaskSchema,
                                    TeamMembershipSchema,
                                    MeetingsSchema)
from app.schemas.types import IdType, TeamsRoleType


T_Stmt = typing.TypeVar("T_Stmt", Select, Update, Delete)


class BaseRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _condition_user_in_team_exists(self,
                                       user_id: IdType,
                                       team_id: IdType) -> Exists:
        user_in_team_exists = exists().where(
            TeamMembership.team_id == team_id,
            TeamMembership.user_id == user_id
            )
        return user_in_team_exists

    def _only_active_users(self, stmt: T_Stmt) -> T_Stmt:
        stmt = stmt.where(Users.is_active == True)  # noqa E712
        return stmt


class UsersRepo(BaseRepo):

    async def register_user(self,
                            name: str,
                            email: str,
                            hashed_password: str) -> UsersSchema:
        user = Users(name=name, email=email, password=hashed_password)
        self.session.add(user)
        await self.session.flush()
        return UsersSchema.model_validate(user)

    async def get_user_by_email(
            self,
            email: str,
            only_active_users: bool = True
            ) -> UsersSchema | None:
        stmt = select(Users).where(Users.email == email)
        if only_active_users:
            stmt = self._only_active_users(stmt=stmt)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            return None
        return UsersSchema.model_validate(user)

    async def get_user_by_id(
            self,
            id: IdType,
            only_active_users: bool = True
            ) -> UsersSchema | None:
        stmt = select(Users).where(Users.id == id)
        if only_active_users:
            stmt = self._only_active_users(stmt=stmt)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            return None
        return UsersSchema.model_validate(user)

    async def update_user_data_by_id(
            self,
            id: IdType,
            update_data: dict,
            only_active_users: bool = True
            ) -> UsersSchema:
        stmt = (update(Users)
                .where(Users.id == id)
                .values(update_data))
        if only_active_users:
            stmt = self._only_active_users(stmt=stmt)
        stmt = stmt.returning(Users)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        return UsersSchema.model_validate(user)

    async def check_is_admin(self, user_id: IdType) -> bool | None:
        stmt = (select(Users.is_admin)
                .where(Users.id==user_id))
        is_admin = await self.session.scalar(stmt)
        return is_admin


class TeamsRepo(BaseRepo):

    async def create_team(self,
                          name: str,
                          manager_id: IdType,
                          description: str | None = None) -> TeamsSchema:
        team = Teams(name=name, description=description)
        """only for admins"""
        self.session.add(team)
        await self.session.flush()
        membership = TeamMembership(
            user_id=manager_id,
            team_id=team.id,
            team_role=TeamsRoles.manager
            )
        self.session.add(membership)
        return TeamsSchema.model_validate(team)

    async def join_team(self, team_id: IdType, user_id: IdType) -> None:
        stmt = (insert(TeamMembership)
                .values(team_id=team_id, user_id=user_id)
                .on_conflict_do_nothing())
        await self.session.execute(stmt)

    async def get_team_by_team_id(self, team_id: IdType) -> TeamsSchema:
        stmt = select().where(Teams.id == team_id)
        team = await self.session.execute(stmt)
        return TeamsSchema.model_validate(team)

    async def check_user_in_team(self,
                                 user_id: IdType,
                                 team_id: IdType) -> bool:
        stmt = select(
            exists().where(
                TeamMembership.team_id == team_id,
                TeamMembership.user_id == user_id
            )
        )
        return bool(await self.session.scalar(stmt))

    async def get_team_membership_by_team_id(
            self,
            team_id: IdType,
            active_members_only: bool = True
            ) -> list[TeamMembershipSchema]:
        stmt = (
            select(Users.id,
                   Users.name,
                   Users.email,
                   TeamMembership.team_role)
            .join(TeamMembership, TeamMembership.user_id == Users.id)
            .join(Teams, TeamMembership.team_id == Teams.id)
            .where(TeamMembership.team_id == team_id)
            )
        if active_members_only:
            stmt = self._only_active_users(stmt=stmt)
        result = await self.session.execute(stmt)
        users = result.mappings().all()
        return [TeamMembershipSchema.model_validate(user) for user in users]

    async def remove_team_member(self,
                                 team_id: IdType,
                                 member_id: IdType) -> IdType | None:
        stmt = (delete(TeamMembership)
                .where(TeamMembership.team_id == team_id,
                       TeamMembership.user_id == member_id)
                .returning(TeamMembership.user_id))
        return await self.session.scalar(stmt)

    async def change_team_member_role(self,
                                      team_id: IdType,
                                      member_id: IdType,
                                      new_role: str) -> IdType | None:
        stmt = (update(TeamMembership)
                .where(TeamMembership.team_id == team_id,
                       TeamMembership.user_id == member_id,)
                .values(team_role=new_role)
                .returning(TeamMembership.id))
        return await self.session.scalar(stmt)

    async def get_team_role(
            self,
            user_id: IdType,
            team_id: IdType
            ) -> TeamsRoleType | None:
        stmt = (select(TeamMembership.team_role)
                .where(TeamMembership.user_id==user_id,
                       TeamMembership.team_id==team_id))
        return await self.session.scalar(stmt)


class TasksRepo(BaseRepo):

    def _due_date_between(self,
                          stmt: T_Stmt,
                          start: dt.date,
                          end: dt.date) -> T_Stmt:
        stmt = stmt.where(Tasks.due_date >= start,
                          Tasks.due_date <= end)
        return stmt

    async def create_task(self,
                          description: str,
                          due_date: dt.date,
                          creator_id: IdType,
                          team_id: IdType) -> None:
        task = Tasks(description=description,
                     creator_id=creator_id,
                     team_id=team_id,
                     due_date=due_date)
        self.session.add(task)
        await self.session.flush()

    async def update_task_by_id(self,
                                team_id: IdType,
                                task_id: IdType,
                                update_data: dict) -> TaskSchema | None:

        stmt = (update(Tasks)
                .where(Tasks.id == task_id,
                       Tasks.team_id == team_id)
                .values(update_data)
                .returning(Tasks))

        result = await self.session.execute(stmt)
        task = result.scalar_one_or_none()
        if task is None:
            return None
        return TaskSchema.model_validate(task)

    async def delete_task_by_id(self,
                                team_id: IdType,
                                task_id: IdType) -> IdType | None:
        stmt = (delete(Tasks)
                .where(Tasks.id == task_id,
                       Tasks.team_id == team_id)
                .returning(Tasks.id))
        return await self.session.scalar(stmt)

    async def get_task_by_task_id(self,
                                  task_id: IdType,
                                  team_id: IdType):
        stmt = (select(Tasks)
                .where(Tasks.id == task_id,
                       Tasks.team_id == team_id))
        task = await self.session.scalar(stmt)
        if task is None:
            return None
        return TaskSchema.model_validate(task)

    async def get_list_tasks_by_user_id(
            self,
            user_id: IdType,
            start: dt.date | None = None,
            end: dt.date | None = None) -> list[TaskSchema]:
        stmt = (select(Tasks)
                .where(Tasks.assignee_id == user_id,
                       Tasks.status != TaskStatus.done))
        if start is not None and end is not None:
            stmt = self._due_date_between(stmt=stmt,
                                          start=start,
                                          end=end)
        result = await self.session.execute(stmt)
        tasks = result.scalars().all()
        return [TaskSchema.model_validate(t) for t in tasks]

    async def user_and_task_in_team(self,
                                    user_id: IdType,
                                    task_id: IdType) -> bool:
        stmt = select(
            exists().where(
                Tasks.id == task_id,
                Tasks.team_id == TeamMembership.team_id,
                TeamMembership.user_id == user_id
                )
            )
        result = await self.session.scalar(stmt)
        return result or False

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


class EvaluationsRepo(BaseRepo):

    async def get_task(
            self,
            task_id: IdType,
            team_id: IdType
            ) -> TaskSchema | None:

        stmt = (select(Tasks)
                .where(Tasks.id==task_id,
                        Tasks.team_id==team_id,
                        Tasks.status==TaskStatus.done))
        task = await self.session.scalar(stmt)
        if task is None: return None
        return TaskSchema.model_validate(task)

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
        return float(avg_evaluation)


class MeetingsRepo(BaseRepo):

    def _meetings_between_start_end(self,
                                    stmt: T_Stmt,
                                    start_meeting: dt.datetime,
                                    end_meeting: dt.datetime) -> T_Stmt:
        stmt = stmt.where(Meetings.start_meeting >= start_meeting,
                          Meetings.start_meeting <= end_meeting)
        return stmt

    async def check_meeting_user_in_team(self,
                                         user_id: IdType,
                                         team_id: IdType,
                                         meeting_id: IdType
                                         ) -> bool:
        """
        Verify that the user and the meeting belong to the same team_id.
        """
        params = {
            'user_id': user_id,
            'team_id': team_id,
            'meeting_id': meeting_id
        }
        stmt = text(
            """
            SELECT EXISTS (
            SELECT 1
            FROM meetings m
            JOIN teams_membership tm
                ON tm.team_id = m.team_id
            WHERE m.id = :meeting_id
                AND m.team_id = :team_id
                AND tm.user_id = :user_id
            )
            """
            )
        result = await self.session.scalar(stmt, params)
        return bool(result)

    async def check_overlap_meetings(self,
                                     user_id: IdType,
                                     start_meeting: dt.datetime,
                                     end_meeting: dt.datetime) -> bool:
        stmt = select(
            exists(
                select(1)
                .select_from(MeetingsParticipants)
                .join(Meetings, MeetingsParticipants.meeting_id == Meetings.id)
                .where(MeetingsParticipants.user_id == user_id,
                       Meetings.start_meeting < end_meeting,
                       Meetings.end_meeting > start_meeting)
                )
            )
        res = await self.session.scalar(stmt)
        return bool(res)

    async def get_meeting_if_user_in_team(
            self,
            user_id: IdType,
            team_id: IdType,
            meeting_id: IdType
            ) -> MeetingsSchema | None:
        """
        Returns the meeting ID, date, and time
        only if the meeting and the user
        belong to {team_id}.
        """
        params = {
            'user_id': user_id,
            'team_id': team_id,
            'meeting_id': meeting_id
        }
        stmt = text(
            """
            SELECT m
            FROM meetings m
            JOIN teams_membership tm
                ON tm.team_id = m.team_id
            WHERE m.id = :meeting_id
                AND m.team_id = :team_id
                AND tm.user_id = :user_id
            """
            )
        result = await self.session.execute(stmt, params)
        meeting = result.mappings().one_or_none()
        if meeting is None:
            return None
        return MeetingsSchema.model_validate(meeting)

    async def create_meeting(self,
                             team_id: IdType,
                             description: str,
                             start_meeting: dt.datetime,
                             end_meeting: dt.datetime) -> IdType:
        meeting_obj = Meetings(description=description,
                               start_meeting=start_meeting,
                               end_meeting=end_meeting,
                               team_id=team_id)
        self.session.add(meeting_obj)
        await self.session.flush()
        return meeting_obj.id

    async def join_meeting(self,
                           user_id: list[IdType] | tuple[IdType] | IdType,
                           meeting_id: IdType) -> None:
        if isinstance(user_id, (list, tuple)):
            for u_id in user_id:
                user_in_meeting = MeetingsParticipants(
                    user_id=u_id,
                    meeting_id=meeting_id
                )
                self.session.add(user_in_meeting)
        else:
            user_in_meeting = MeetingsParticipants(
                user_id=user_id,
                meeting_id=meeting_id
            )
            self.session.add(user_in_meeting)

    async def delete_meeting(
            self,
            meeting_id: IdType,
            team_id: IdType
            ) -> None:
        stmt = (delete(Meetings)
                .where(Meetings.id == meeting_id,
                       Meetings.team_id == team_id))
        await self.session.execute(stmt)

    async def get_list_meetings_by_team_id(
            self,
            team_id: IdType
            ) -> list[MeetingsSchema]:
        stmt = select(Meetings).where(Meetings.team_id == team_id)
        result = await self.session.execute(stmt)
        meetings = result.scalars().all()
        return [MeetingsSchema.model_validate(meeting) for meeting in meetings]

    async def get_list_meetings_by_user_id(
            self,
            user_id: IdType,
            start_meeting: dt.datetime | None = None,
            end_meeting: dt.datetime | None = None
            ) -> list[MeetingsSchema]:
        stmt = (select(Meetings)
                .join(MeetingsParticipants,
                      Meetings.id == MeetingsParticipants.meeting_id)
                .where(MeetingsParticipants.user_id == user_id))
        if start_meeting is not None and end_meeting is not None:
            stmt = self._meetings_between_start_end(
                stmt=stmt,
                start_meeting=start_meeting,
                end_meeting=end_meeting)
        result = await self.session.execute(stmt)
        meetings = result.scalars().all()
        return [MeetingsSchema.model_validate(meeting) for meeting in meetings]

    async def get_meeting_by_meeting_id(
            self,
            meeting_id: IdType
            ) -> MeetingsSchema | None:
        stmt = (select(Meetings)
                .where(Meetings.id == meeting_id))
        result = await self.session.execute(stmt)
        meeting = result.scalar_one_or_none()
        if meeting is None:
            return None
        return MeetingsSchema.model_validate(meeting)
