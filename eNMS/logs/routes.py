from flask import jsonify, render_template, request
from re import search

from eNMS import db
from eNMS.automation.models import Job
from eNMS.base.custom_base import factory
from eNMS.base.helpers import fetch, get, post
from eNMS.base.properties import pretty_names
from eNMS.logs import bp
from eNMS.logs.forms import LogAutomationForm, LogFilteringForm
from eNMS.logs.models import Log, LogRule


@get(bp, '/log_management', 'Logs Section')
def log_management():
    log_filtering_form = LogFilteringForm(request.form)
    return render_template(
        'log_management.html',
        log_filtering_form=log_filtering_form,
        names=pretty_names,
        fields=('source', 'content'),
        logs=Log.serialize()
    )


@get(bp, '/log_automation', 'Logs Section')
def syslog_automation():
    log_automation_form = LogAutomationForm(request.form)
    log_automation_form.jobs.choices = Job.choices()
    return render_template(
        'log_automation.html',
        log_automation_form=log_automation_form,
        names=pretty_names,
        fields=('name', 'source', 'content'),
        log_rules=LogRule.serialize()
    )


@post(bp, '/delete_log/<log_id>', 'Edit Logs Section')
def delete_log(log_id):
    log = fetch(Log, id=log_id)
    db.session.delete(log)
    db.session.commit()
    return jsonify({'success': True})


@post(bp, '/filter_logs', 'Edit Logs Section')
def filter_logs():
    logs = [log for log in Log.serialize() if all(
        # if the regex property is not in the request, the
        # regex box is unticked and we only check that the values of the
        # filters are contained in the values of the log
        request.form[prop] in str(val) if not prop + 'regex' in request.form
        # if it is ticked, we use re.search to check that the value
        # of the device property matches the regular expression,
        # providing that the property field in the form is not empty
        # (empty field <==> property ignored)
        else search(request.form[prop], str(val)) for prop, val in log.items()
        if prop in request.form and request.form[prop]
    )]
    return jsonify(logs)


@post(bp, '/get_log_rule/<log_rule_id>', 'Logs Section')
def get_log_rule(log_rule_id):
    return jsonify(fetch(LogRule, id=log_rule_id).serialized)


@post(bp, '/save_log_rule', 'Edit Logs Section')
def save_log_rule():
    data = request.form.to_dict()
    data['jobs'] = [
        fetch(Job, id=id) for id in request.form.getlist('jobs')
    ]
    log_rule = factory(LogRule, **data)
    db.session.commit()
    return jsonify(log_rule.serialized)


@post(bp, '/delete_log_rule/<log_id>', 'Edit Logs Section')
def delete_log_rule(log_id):
    log_rule = fetch(LogRule, id=log_id)
    db.session.delete(log_rule)
    db.session.commit()
    return jsonify({'success': True})
