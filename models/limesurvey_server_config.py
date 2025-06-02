import xmlrpc.client
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging
import re
import requests
from urllib.parse import urljoin

_logger = logging.getLogger(__name__)

class LimeSurveyServerConfig(models.Model):
    _name = 'limesurvey.server.config'
    _description = 'LimeSurvey Server Configuration'
    _inherit = ['mail.thread']
    _rec_name = 'name'
    _order = 'name'

    name = fields.Char(
        string='Name',
        required=True,
        tracking=True,
        help='Name of the LimeSurvey server configuration',
    )
    api_url = fields.Char(
        string='API URL',
        required=True,
        tracking=True,
    )
    username = fields.Char(
        string='Username',
        required=True,
        tracking=True,
    )
    password = fields.Char(
        string='Password',
        required=True,
        tracking=True,
        password=True,
    )
    session_key = fields.Char(
        string='Session Key',
        readonly=True,
        copy=False,
        groups='base.group_system',
        help='LimeSurvey API session key',
    )
    connected = fields.Boolean(
        string='Connected',
        default=False,
        readonly=True,
        tracking=True,
        help='Indicates if the connection with LimeSurvey server is established',
    )

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Server configuration name must be unique!')
    ]

    @api.constrains('api_url')
    def _check_api_url(self):
        for record in self:
            if not record.api_url:
                continue
                
            api_url = record.api_url.strip()
            
            # Verify URL starts with http:// or https://
            if not re.match(r'^https?://', api_url):
                raise ValidationError(_('API URL must start with http:// or https://'))

    def _get_api_url(self):
        """Build the complete RemoteControl API URL."""
        base_url = self.api_url.rstrip('/')
        base_url = re.sub(r'/index\.php.*', '', base_url)
        base_url = re.sub(r'/admin.*', '', base_url)
        
        # Construct the XML-RPC endpoint URL
        api_url = urljoin(f"{base_url}/", "index.php/admin/remotecontrol")
        _logger.info('Using API URL: %s', api_url)
        return api_url

    def _get_client(self):
        """Create and return an XML-RPC client for the LimeSurvey API."""
        api_url = self._get_api_url()
        
        try:
            # First verify the endpoint is accessible
            response = requests.get(api_url, timeout=5)
            if response.status_code != 200:
                raise ValidationError(_(
                    'Cannot access LimeSurvey API at %(url)s\n\n'
                    'Status code: %(code)s\n'
                    'Response: %(response)s',
                    url=api_url,
                    code=response.status_code,
                    response=response.text[:200]
                ))
            
            # Create XML-RPC client
            _logger.info('Creating XML-RPC client for %s', api_url)
            return xmlrpc.client.ServerProxy(api_url)
            
        except requests.exceptions.RequestException as e:
            raise ValidationError(_(
                'Cannot connect to LimeSurvey at %(url)s\n\n'
                'Error: %(error)s',
                url=api_url,
                error=str(e)
            ))
        except Exception as e:
            raise ValidationError(_(
                'Failed to initialize LimeSurvey API client\n\n'
                'URL: %(url)s\n'
                'Error: %(error)s',
                url=api_url,
                error=str(e)
            ))

    def connect(self):
        """Connect to LimeSurvey server and get session key."""
        self.ensure_one()
        
        if not all([self.api_url, self.username, self.password]):
            message = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Connection Error'),
                    'message': _('Please provide all required connection information.'),
                    'type': 'danger',
                    'sticky': False,
                }
            }
            return message

        try:
            client = self._get_client()
            _logger.info('Attempting to get session key...')
            
            try:
                result = client.get_session_key(self.username, self.password)
                _logger.info('Got response from get_session_key')
            except xmlrpc.client.Fault as e:
                _logger.error('XML-RPC fault: %s', str(e))
                message = {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Connection Failed'),
                        'message': _('LimeSurvey API error: %s\n\nPlease verify your credentials and that the RemoteControl API is enabled.', str(e)),
                        'type': 'danger',
                        'sticky': True,
                    }
                }
                raise ValidationError(message)
            
            if isinstance(result, str):  # Successful connection
                self.write({
                    'session_key': result,
                    'connected': True
                })
                self.message_post(
                    body=_('Successfully connected to LimeSurvey server.'),
                    message_type='notification'
                )
                _logger.info('Successfully connected to LimeSurvey')
                
                # Synchroniser les formulaires après la connexion
                self.sync_surveys()
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Success'),
                        'message': _('Successfully connected to LimeSurvey server and synchronized forms.'),
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                _logger.error('Invalid response format: %s', result)
                message = {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Connection Failed'),
                        'message': _('Invalid response from LimeSurvey server.'),
                        'type': 'danger',
                        'sticky': True,
                    }
                }
                raise UserError(message)

        except Exception as e:
            _logger.error('Connection failed: %s', str(e))
            self.write({'connected': False, 'session_key': False})
            error_msg = _('Failed to connect to LimeSurvey: %s', str(e))
            self.message_post(
                body=error_msg,
                message_type='notification'
            )
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Connection Failed'),
                    'message': error_msg,
                    'type': 'danger',
                    'sticky': True,
                }
            }

    def disconnect(self):
        """Release the LimeSurvey session."""
        self.ensure_one()
        
        if not self.session_key:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Info'),
                    'message': _('Already disconnected.'),
                    'type': 'info',
                    'sticky': False,
                }
            }

        try:
            client = self._get_client()
            try:
                result = client.release_session_key(self.session_key)
            except xmlrpc.client.Fault as e:
                _logger.warning('Failed to release session key: %s', str(e))
                result = False
            
            if result:
                _logger.info('Successfully released session key')
            else:
                _logger.warning('Failed to release session key')
            
        except Exception as e:
            _logger.error('Error while disconnecting: %s', str(e))
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Warning'),
                    'message': _('Error while disconnecting: %s', str(e)),
                    'type': 'warning',
                    'sticky': True,
                }
            }
        
        # Always clear the session, even if the API call fails
        self.write({
            'session_key': False,
            'connected': False
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Successfully disconnected from LimeSurvey server.'),
                'type': 'success',
                'sticky': False,
            }
        }

    def unlink(self):
        """Ensure proper disconnection before deletion."""
        for record in self:
            record.disconnect()
        return super().unlink()

    @api.model
    def create(self, vals):
        """Override create to test connection on creation if all credentials are provided."""
        if 'api_url' in vals and vals.get('api_url'):
            vals['api_url'] = vals['api_url'].strip().rstrip('/')
            
        record = super().create(vals)
        if all([record.api_url, record.username, record.password]):
            try:
                record.connect()
            except (UserError, ValidationError):
                pass
        return record

    def write(self, vals):
        """Override write to test connection if credentials are updated."""
        if 'api_url' in vals and vals.get('api_url'):
            vals['api_url'] = vals['api_url'].strip().rstrip('/')
        
        result = super().write(vals)
        if any(field in vals for field in ['api_url', 'username', 'password']):
            for record in self:
                try:
                    record.connect()
                except (UserError, ValidationError):
                    pass
        return result 

    def _call_api(self, method, params=None):
        """
        Appelle une méthode de l'API LimeSurvey.
        
        Args:
            method (str): Nom de la méthode à appeler
            params (list): Liste des paramètres à passer à la méthode
            
        Returns:
            mixed: Résultat de l'appel API ou False en cas d'erreur
        """
        if params is None:
            params = []
            
        try:
            client = self._get_client()
            _logger.info("Appel de la méthode %s avec les paramètres: %s", method, params)
            
            # Appel de la méthode de l'API
            api_method = getattr(client, method)
            result = api_method(*params)
            
            # Vérification du résultat
            if isinstance(result, dict) and result.get('status') == 'error':
                _logger.error("Erreur API LimeSurvey: %s", result.get('message'))
                return False
                
            return result
            
        except xmlrpc.client.Fault as e:
            _logger.error("Erreur XMLRPC lors de l'appel à %s: %s", method, str(e))
            return False
        except Exception as e:
            _logger.error("Erreur lors de l'appel à %s: %s", method, str(e))
            return False

    def _get_session_key(self):
        """Obtient une session key de l'API LimeSurvey."""
        try:
            client = self._get_client()
            session_key = client.get_session_key(self.username, self.password)
            if isinstance(session_key, str):
                return session_key
            _logger.error("Session key invalide reçue: %s", session_key)
            return False
        except Exception as e:
            _logger.error("Erreur lors de l'obtention de la session key: %s", str(e))
            return False

    def _release_session_key(self, session_key):
        """Libère une session key de l'API LimeSurvey."""
        try:
            client = self._get_client()
            result = client.release_session_key(session_key)
            if not result:
                _logger.warning("Échec de la libération de la session key")
            return result
        except Exception as e:
            _logger.error("Erreur lors de la libération de la session key: %s", str(e))
            return False

    def sync_surveys(self):
        """Synchronise les formulaires depuis LimeSurvey vers Odoo"""
        _logger.info("Début de la synchronisation des surveys")
        for server in self:
            if not server.connected:
                _logger.warning("Serveur %s non connecté, synchronisation ignorée", server.name)
                continue
            
            session_key = False
            try:
                # Connexion à l'API LimeSurvey
                session_key = server._get_session_key()
                if not session_key:
                    _logger.error("Impossible d'obtenir une session key pour le serveur %s", server.name)
                    continue

                # Récupération de la liste des surveys
                _logger.info("Appel de list_surveys pour le serveur %s", server.name)
                surveys = server._call_api('list_surveys', [session_key])
                
                if not surveys:
                    _logger.warning("Aucun survey trouvé sur le serveur %s", server.name)
                    continue

                _logger.info("Nombre de surveys trouvés : %s", len(surveys))
                for survey in surveys:
                    _logger.info("Traitement du survey : %s", survey.get('surveyls_title'))
                    # Création ou mise à jour du survey dans Odoo
                    survey_values = {
                        'sid': survey.get('sid'),
                        'title': survey.get('surveyls_title'),
                        'language': survey.get('language'),
                        'owner_id': survey.get('owner_id'),
                        'active': survey.get('active') == 'Y',
                        'server_id': server.id,
                    }
                    
                    existing_survey = self.env['admission.survey.template'].search([
                        ('sid', '=', survey.get('sid')),
                        ('server_id', '=', server.id)
                    ], limit=1)
                    
                    if existing_survey:
                        _logger.info("Mise à jour du survey existant : %s", survey.get('surveyls_title'))
                        existing_survey.write(survey_values)
                    else:
                        _logger.info("Création d'un nouveau survey : %s", survey.get('surveyls_title'))
                        self.env['admission.survey.template'].create(survey_values)

            except Exception as e:
                _logger.error("Erreur lors de la synchronisation des surveys pour le serveur %s: %s", server.name, str(e))
                raise
            finally:
                if session_key:
                    try:
                        server._release_session_key(session_key)
                    except Exception as e:
                        _logger.warning("Erreur lors de la libération de la session: %s", str(e))

        _logger.info("Fin de la synchronisation des surveys")
        return True 