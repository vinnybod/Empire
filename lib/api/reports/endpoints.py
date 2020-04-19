from flask.views import MethodView
from flask_smorest import Blueprint

from lib.api.reports.schemas import ReportsSchema
from lib.database.base import Session

repo_blp = Blueprint(
    'reports', 'reports', url_prefix='/api/reports',
    description='Reporting'
)


# Todo vr: reports is going to probably split out to "logging" and "reports"
#  where logging contains every entry in the table and reports is filtered down to
#  taskings like we have here. Because these responses grow so large, we're going to need paging
#  In addition, with the way the tables are set up, we may need to use raw sql instead of sqlalchemy
#  Waiting for direction from Coin/Hubble.
@repo_blp.route('/')
class ReportView(MethodView):

    @repo_blp.response(ReportsSchema, code=200)
    def get(self):
        """
        Returns JSON describing the reporting events from the backend database.
        """
        # Add filters for agent, event_type, and MAYBE a like filter on msg
        reporting_raw = Session().connection().execute('''
        SELECT
                reporting.time_stamp,
                event_type,
                u.username,
                substr(reporting.name, pos+1) as agent_name,
                a.hostname,
                taskID,
                t.data as "Task",
                r.data as "Results"
            FROM
            (
                SELECT
                    time_stamp,
                    event_type,
                    name,
                    instr(name, '/') as pos,
                    taskID
                FROM reporting
                WHERE name LIKE 'agent%'
                AND reporting.event_type == 'task' OR reporting.event_type == 'checkin') reporting
            LEFT OUTER JOIN taskings t on (reporting.taskID = t.id) AND (agent_name = t.agent)
            LEFT OUTER JOIN results r on (reporting.taskID = r.id) AND (agent_name = r.agent)
            JOIN agents a on agent_name = a.session_id
            LEFT OUTER JOIN users u on t.user_id = u.id
            ORDER BY reporting.time_stamp DESC
        ''')
        reporting_events = []

        for reportingEvent in reporting_raw:
            [time_stamp, event_type, user_name, agent_name, host_name, taskID, task, results] = reportingEvent
            reporting_events.append(
                {"timestamp": time_stamp, "event_type": event_type, "username": user_name, "agent_name": agent_name,
                 "host_name": host_name, "taskID": taskID, "task": task, "results": results})

        return {'reporting': reporting_events}
