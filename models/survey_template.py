from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AdmissionSurveyTemplate(models.Model):
    _name = 'admission.survey.template'
    _description = 'Modèle de Formulaire LimeSurvey'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    sid = fields.Integer(string='ID LimeSurvey', required=True, tracking=True)
    title = fields.Char(string='Titre', required=True, tracking=True)
    description = fields.Html(string='Description', tracking=True, sanitize=True)
    language = fields.Char(string='Langue', tracking=True)
    owner_id = fields.Integer(string='ID Créateur', tracking=True)
    active = fields.Boolean(string='Actif', default=True, tracking=True)
    server_id = fields.Many2one('limesurvey.server.config', string='Serveur LimeSurvey', required=True, tracking=True)
    
    # Nouveaux champs
    public_url = fields.Char(
        string='URL Publique',
        tracking=True,
        help="URL publique pour accéder au formulaire"
    )
    response_count = fields.Integer(
        string='Nombre de réponses',
        tracking=True,
        help="Nombre total de réponses reçues"
    )
    complete_response_count = fields.Integer(
        string='Réponses complètes',
        tracking=True,
        help="Nombre de réponses complètement remplies"
    )
    survey_type = fields.Selection([
        ('admission', 'Admission'),
        ('satisfaction', 'Satisfaction'),
        ('evaluation', 'Évaluation'),
        ('feedback', 'Retour d\'expérience'),
        ('other', 'Autre')
    ], string='Type', required=True, default='admission', tracking=True)
    start_date = fields.Datetime(
        string='Date de début',
        tracking=True,
        help="Date d'ouverture du formulaire"
    )
    end_date = fields.Datetime(
        string='Date de fin',
        tracking=True,
        help="Date de fermeture du formulaire"
    )
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('active', 'Actif'),
        ('expired', 'Expiré'),
        ('closed', 'Fermé')
    ], string='État', default='draft', tracking=True, required=True)

    _sql_constraints = [
        ('unique_survey_per_server', 
         'UNIQUE(sid, server_id)',
         'Un formulaire avec cet ID existe déjà pour ce serveur LimeSurvey!')
    ]

    @api.onchange('active', 'start_date', 'end_date')
    def _onchange_state(self):
        """Met à jour l'état du formulaire en fonction des dates et de son statut actif"""
        for record in self:
            if not record.active:
                record.state = 'closed'
            elif not record.start_date:
                record.state = 'draft'
            elif record.end_date and record.end_date < fields.Datetime.now():
                record.state = 'expired'
            elif record.start_date <= fields.Datetime.now():
                record.state = 'active'
            else:
                record.state = 'draft'

    def action_view_public_url(self):
        """Ouvre l'URL publique dans un nouvel onglet"""
        self.ensure_one()
        if not self.public_url:
            raise ValidationError(_("Aucune URL publique disponible pour ce formulaire."))
        return {
            'type': 'ir.actions.act_url',
            'url': self.public_url,
            'target': 'new'
        }

    @api.model
    def create(self, vals):
        """Surcharge de la création pour définir l'état initial"""
        if 'state' not in vals:
            vals['state'] = self._get_default_state(vals)
        return super().create(vals)

    def write(self, vals):
        """Surcharge de l'écriture pour mettre à jour l'état si nécessaire"""
        result = super().write(vals)
        # Mise à jour de l'état si des champs pertinents ont été modifiés
        if any(field in vals for field in ['active', 'start_date', 'end_date']):
            self._onchange_state()
        return result

    def _get_default_state(self, vals):
        """Détermine l'état initial en fonction des valeurs fournies"""
        if not vals.get('active', True):
            return 'closed'
        if not vals.get('start_date'):
            return 'draft'
        start_date = fields.Datetime.from_string(vals['start_date'])
        end_date = vals.get('end_date') and fields.Datetime.from_string(vals['end_date'])
        now = fields.Datetime.now()
        if end_date and end_date < now:
            return 'expired'
        if start_date <= now:
            return 'active'
        return 'draft' 