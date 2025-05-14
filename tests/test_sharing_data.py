import pytest
from datetime import datetime, timedelta
from app.models import User, Summary, SharedSummary
from app.extensions import db

# TODO: share endpoint, model creation, invalid recipient, duplicate share


# -------------------------------
# Sanity check
# -------------------------------

def james_n_sacha_appear(client, two_users):
    user1, user2 = two_users

    assert user1.username == "james"
    assert user2.username == "sacha"

def test_summary_fields_are_saved(some_summaries):
    s1, s2 = some_summaries
    assert s1.total_buy == 100.0
    assert s1.total_sell == 200.0
    assert s2.total_buy == 300.0
    assert s2.total_sell == 400.0

def test_summary_gets_an_id(app):
    sum = Summary(user_id=1, total_buy=1.23, total_sell=4.56)
    db.session.add(sum)
    db.session.commit()
    assert sum.id is not None
    assert isinstance(sum.id, int)

def test_summaries_belong_to_jmaes(two_users, some_summaries):
    james, _ = two_users
    for summary in some_summaries:
        assert summary.user_id == james.id

def test_sacha_is_summaryless (two_users):
    _, sacha = two_users
    summaries = Summary.query.filter_by(user_id=sacha.id).all()
    assert summaries == []

def test_summary_totals(some_summaries):
    total_buy = sum(s.total_buy for s in some_summaries)
    total_sell = sum(s.total_sell for s in some_summaries)

    assert total_buy == 100 + 300
    assert total_sell == 200 + 400

def test_correct_amount_of_summaries(some_summaries):
    assert len(some_summaries) == 2

def test_created_summaries_are_saved_in_database(some_summaries):
    # Get the database-assigned IDs of the summaries just created
    created_ids = [summary.id for summary in some_summaries]

    # Fetch all Summary records from the DB that match those IDs
    # janky SQLAlchemy syntax note: need to revise...
    summaries_in_db = Summary.query.filter(Summary.id.in_(created_ids)).all()

    # Make sure both summaries were actually saved and can be retrieved
    assert len(summaries_in_db) == 2

# -------------------------------
# Models
# -------------------------------

@pytest.fixture
def two_users_and_summary(app):

    # Create two users, one summary for user1

    james = User(username="james", email="james@example.com")
    james.set_password("pw1")
    sacha   = User(username="sacha",   email="sacha@example.com")
    sacha.set_password("pw2")
    db.session.add_all([james, sacha])
    db.session.commit()

    summary = Summary(user_id=james.id, total_buy=100.0, total_sell=150.0)
    db.session.add(summary)
    db.session.commit()

    return james, sacha, summary


def test_create_and_query_shared_summary(app, two_users_and_summary):
    james, sacha, summary = two_users_and_summary

    share = SharedSummary(
        summary_id=summary.id,
        from_user_id=james.id,
        to_user_id=sacha.id
    )
    db.session.add(share)
    db.session.commit()

    # It got an ID and correct Foreign Keys
    assert share.id is not None
    assert share.summary_id    == summary.id
    assert share.from_user_id  == james.id
    assert share.to_user_id    == sacha.id

    now = datetime.utcnow()
    assert isinstance(share.timestamp, datetime)
    assert now - share.timestamp < timedelta(seconds=5)

@pytest.fixture
def two_users_and_summary(app, two_users):
    # –––––– Create two users, one summary for user1 ––––––
    james, sacha = two_users
    db.session.add_all([james, sacha])
    db.session.commit()

    summary = Summary(user_id=james.id, total_buy=100.0, total_sell=150.0)
    db.session.add(summary)
    db.session.commit()

    return james, sacha, summary


def test_create_and_query_shared_summary(app, two_users_and_summary):
    james, sacha, summary = two_users_and_summary

    share = SharedSummary(
        summary_id=summary.id,
        from_user_id=james.id,
        to_user_id=sacha.id
    )
    db.session.add(share)
    db.session.commit()

    # It got an ID and correct FKs
    assert share.id is not None
    assert share.summary_id    == summary.id
    assert share.from_user_id  == james.id
    assert share.to_user_id    == sacha.id

    # timestamp default is “now”
    now = datetime.now()
    assert isinstance(share.timestamp, datetime)
    assert now - share.timestamp < timedelta(seconds=5)