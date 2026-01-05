"""Tests pour le client LLM."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.llm_client import LLMClient, create_llm_client


class TestLLMClient:
    """Tests pour la classe LLMClient."""

    def test_llm_client_init(self):
        """Test l'initialisation du client."""
        client = LLMClient(
            api_key="test_key",
            base_url="https://test.com/v1",
            model="test-model",
            timeout=20,
            max_retries=2
        )
        
        assert client.api_key == "test_key"
        assert client.base_url == "https://test.com/v1"
        assert client.model == "test-model"
        assert client.timeout == 20
        assert client.max_retries == 2

    def test_llm_client_init_no_api_key(self):
        """Test l'initialisation sans clé API."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="API key manquante"):
                LLMClient()

    @patch('src.llm_client.requests.post')
    def test_make_request_success(self, mock_post):
        """Test une requête réussie."""
        # Mock de la réponse
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Ceci est une réponse de test"
                    }
                }
            ]
        }
        mock_post.return_value = mock_response

        client = LLMClient(api_key="test_key")
        messages = [{"role": "user", "content": "Test"}]
        
        response = client._make_request(messages)
        
        assert response == "Ceci est une réponse de test"
        assert mock_post.called

    @patch('src.llm_client.requests.post')
    def test_make_request_timeout(self, mock_post):
        """Test le timeout de requête."""
        import requests
        mock_post.side_effect = requests.exceptions.Timeout()

        client = LLMClient(api_key="test_key", max_retries=0)
        messages = [{"role": "user", "content": "Test"}]
        
        response = client._make_request(messages)
        
        assert response is None

    @patch('src.llm_client.requests.post')
    def test_make_request_retry(self, mock_post):
        """Test le mécanisme de retry."""
        import requests
        # Premier appel échoue, deuxième réussit
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Succès au 2e essai"}}]
        }
        
        mock_post.side_effect = [
            requests.exceptions.Timeout(),
            mock_response
        ]

        client = LLMClient(api_key="test_key", max_retries=1)
        messages = [{"role": "user", "content": "Test"}]
        
        response = client._make_request(messages)
        
        assert response == "Succès au 2e essai"
        assert mock_post.call_count == 2

    @patch('src.llm_client.requests.post')
    def test_get_tutor_explanation(self, mock_post):
        """Test l'obtention d'une explication tuteur."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Explication pédagogique"}}]
        }
        mock_post.return_value = mock_response

        client = LLMClient(api_key="test_key")
        explanation = client.get_tutor_explanation("Quelle est la capitale de la France?")
        
        assert explanation == "Explication pédagogique"
        
        # Vérifier que le prompt système est bien inclus
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        assert len(payload['messages']) == 2
        assert payload['messages'][0]['role'] == 'system'
        assert 'tuteur' in payload['messages'][0]['content'].lower()

    @patch('src.llm_client.requests.post')
    def test_get_final_answer(self, mock_post):
        """Test l'obtention de la réponse finale."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "La réponse est Paris"}}]
        }
        mock_post.return_value = mock_response

        client = LLMClient(api_key="test_key")
        answer = client.get_final_answer(
            "Quelle est la capitale de la France?",
            "Voici une explication..."
        )
        
        assert answer == "La réponse est Paris"
        
        # Vérifier que le message de révélation est inclus
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        assert len(payload['messages']) >= 3

    @patch('src.llm_client.requests.post')
    def test_request_error_handling(self, mock_post):
        """Test la gestion des erreurs de requête."""
        import requests
        mock_post.side_effect = requests.exceptions.RequestException("Erreur réseau")

        client = LLMClient(api_key="test_key", max_retries=0)
        messages = [{"role": "user", "content": "Test"}]
        
        response = client._make_request(messages)
        
        assert response is None

    @patch('src.llm_client.requests.post')
    def test_malformed_response(self, mock_post):
        """Test avec une réponse mal formée."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"invalid": "structure"}
        mock_post.return_value = mock_response

        client = LLMClient(api_key="test_key")
        messages = [{"role": "user", "content": "Test"}]
        
        response = client._make_request(messages)
        
        assert response is None


class TestFactoryFunction:
    """Tests pour la fonction factory."""

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'env_key', 'LLM_MODEL': 'gpt-4'})
    def test_create_llm_client_from_env(self):
        """Test la création du client depuis les variables d'environnement."""
        client = create_llm_client()
        
        assert client.api_key == 'env_key'
        assert client.model == 'gpt-4'

    def test_create_llm_client_with_params(self):
        """Test la création avec des paramètres explicites."""
        client = create_llm_client(
            api_key="custom_key",
            base_url="https://custom.api.com",
            model="custom-model"
        )
        
        assert client.api_key == "custom_key"
        assert client.base_url == "https://custom.api.com"
        assert client.model == "custom-model"
