import json

from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for

from app import db
from app.journal.models import JournalCategory, Journal

mod = Blueprint('journal', __name__, url_prefix='/journal')

@mod.route('/view/')
def view():
    journal_id = request.args.get('journal_id', 0)
    if journal_id == 0:
        return render_template('404.html'), 404

    journal = Journal.query.filter_by(id=journal_id).first()
    if journal is None:
        return render_template('404.html'), 404

    if journal.is_activated == 0 and not g.user.is_admin:
        return render_template('404.html'), 404

    return render_template("journal/view.html", journal=journal.to_dict(include_category=True, include_created_user=True, include_last_edited_user=True))