from odoo import models, fields, api

class LimeSurveyConfig(models.Model):
    _name = 'limesurvey.config'
    _description = 'LimeSurvey Configuration'
    _inherit = ['mail.thread']
    _order = 'open_date desc, id desc'

    name = fields.Char(
        string='Name',
        required=True,
        tracking=True,
        index=True,
    )
    remote_id = fields.Integer(
        string='LimeSurvey ID',
        required=True,
        tracking=True,
        index=True,
    )
    form_type = fields.Selection(
        [
            ('student', 'Student'),
            ('professional', 'Professional'),
            ('international', 'International'),
            ('other', 'Other'),
        ],
        string='Form Type',
        required=True,
        tracking=True,
        index=True,
    )
    survey_url = fields.Char(
        string='Survey URL',
        tracking=True,
    )
    open_date = fields.Datetime(
        string='Opening Date',
        tracking=True,
        index=True,
    )
    close_date = fields.Datetime(
        string='Closing Date',
        tracking=True,
        index=True,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        tracking=True,
        index=True,
    )

    _sql_constraints = [
        ('unique_remote_id',
         'UNIQUE(remote_id)',
         'The LimeSurvey ID must be unique!'),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        return super().create(vals_list) 