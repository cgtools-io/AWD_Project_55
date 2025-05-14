from flask_wtf import FlaskForm
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired

class ShareForm(FlaskForm):
    # summary_id is current Summary.id column
    summary_id = SelectField(
        "Select Data to Share",
        coerce=int,
        validators=[DataRequired()]
    )

    # recipient id is the User.id sharing with
    recipient_id = SelectField(
        "User ID / Recipient",
        coerce=int,
        validators=[DataRequired()]
    )

    #Renders as the Share button
    submit = SubmitField("Share")