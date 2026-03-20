# -*- coding: utf-8 -*-
"""
Unit tests for SeeActAgent class.

This test suite covers the core functionality of the SeeActAgent including:
- Initialization with various configurations
- Prompt generation
- Action space management
- Task management
- Browser session handling
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch, mock_open
import pytest
import toml

# Import the class to test
from seeact.agent import SeeActAgent


class TestSeeActAgentInitialization:
    """Test suite for SeeActAgent initialization."""

    @patch('seeact.agent.engine_factory')
    @patch('os.makedirs')
    def test_should_initialize_with_default_config_when_no_config_file_provided(
        self, mock_makedirs, mock_engine_factory
    ):
        """Test that agent initializes correctly with default configuration."""
        # Arrange
        mock_engine = MagicMock()
        mock_engine_factory.return_value = mock_engine
        
        # Act
        agent = SeeActAgent(
            config_path=None,
            save_file_dir="test_dir",
            default_task="Test task",
            default_website="https://test.com"
        )
        
        # Assert
        assert agent.config is not None
        assert agent.config["basic"]["default_task"] == "Test task"
        assert agent.config["basic"]["default_website"] == "https://test.com"
        assert agent.config["basic"]["save_file_dir"] == "test_dir"
        assert agent.complete_flag is False
        assert len(agent.tasks) == 1
        assert agent.tasks[0] == "Test task"
        mock_makedirs.assert_called()

    @patch('seeact.agent.engine_factory')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    @patch('toml.load')
    def test_should_load_configuration_from_toml_file(
        self, mock_toml_load, mock_file, mock_makedirs, mock_engine_factory
    ):
        """Test that agent loads configuration from TOML file correctly."""
        # Arrange
        mock_engine = MagicMock()
        mock_engine_factory.return_value = mock_engine
        
        test_config = {
            "basic": {
                "save_file_dir": "config_dir",
                "default_task": "Config task",
                "default_website": "https://config.com",
                "crawler_mode": False,
                "crawler_max_steps": 10
            },
            "agent": {
                "input_info": ["screenshot"],
                "grounding_strategy": "text_choice_som",
                "max_auto_op": 50,
                "max_continuous_no_op": 5,
                "highlight": False
            },
            "openai": {
                "rate_limit": -1,
                "model": "gpt-4o",
                "api_base": "https://api.openai.com/v1",
                "api_key": "test-key",
                "temperature": 0.9
            }
        }
        mock_toml_load.return_value = test_config
        
        # Act
        agent = SeeActAgent(config_path="/fake/path/config.toml")
        
        # Assert
        assert agent.config["basic"]["default_task"] == "Config task"
        assert agent.config["basic"]["default_website"] == "https://config.com"
        mock_file.assert_called_once_with("/fake/path/config.toml", 'r')

    @patch('seeact.agent.engine_factory')
    @patch('os.makedirs')
    def test_should_create_necessary_directories_for_agent_files(
        self, mock_makedirs, mock_engine_factory
    ):
        """Test that agent creates necessary directories during initialization."""
        # Arrange
        mock_engine = MagicMock()
        mock_engine_factory.return_value = mock_engine
        
        # Act
        agent = SeeActAgent(save_file_dir="test_output")
        
        # Assert
        mock_makedirs.assert_called()
        assert agent.main_path is not None
        assert "test_output" in agent.main_path


class TestSeeActAgentPrompts:
    """Test suite for prompt generation and management."""

    @patch('seeact.agent.engine_factory')
    @patch('os.makedirs')
    def test_should_initialize_prompts_correctly_for_text_choice_som_strategy(
        self, mock_makedirs, mock_engine_factory
    ):
        """Test that prompts are initialized correctly for text_choice_som strategy."""
        # Arrange
        mock_engine = MagicMock()
        mock_engine_factory.return_value = mock_engine
        
        # Act
        agent = SeeActAgent(grounding_strategy="text_choice_som")
        
        # Assert
        assert "system_prompt" in agent.prompts
        assert "action_space" in agent.prompts
        assert "question_description" in agent.prompts
        assert "referring_description" in agent.prompts
        assert "element_format" in agent.prompts
        assert "action_format" in agent.prompts
        assert "value_format" in agent.prompts

    @patch('seeact.agent.engine_factory')
    @patch('os.makedirs')
    def test_should_initialize_prompts_correctly_for_pixel_2_stage_strategy(
        self, mock_makedirs, mock_engine_factory
    ):
        """Test that prompts are initialized correctly for pixel_2_stage strategy."""
        # Arrange
        mock_engine = MagicMock()
        mock_engine_factory.return_value = mock_engine
        
        # Act
        agent = SeeActAgent(grounding_strategy="pixel_2_stage")
        
        # Assert
        assert "system_prompt" in agent.prompts
        assert "question_description" in agent.prompts
        # pixel_2_stage has different prompt structure
        assert "action_space" not in agent.prompts

    @patch('seeact.agent.engine_factory')
    @patch('os.makedirs')
    @patch('seeact.agent.generate_new_query_prompt')
    @patch('seeact.agent.generate_new_referring_prompt')
    def test_should_generate_proper_prompts_with_task_and_choices(
        self, mock_referring_prompt, mock_query_prompt, mock_makedirs, mock_engine_factory
    ):
        """Test that generate_prompt creates correct prompt structure."""
        # Arrange
        mock_engine = MagicMock()
        mock_engine_factory.return_value = mock_engine
        mock_query_prompt.return_value = ["system", "query"]
        mock_referring_prompt.return_value = "referring"
        
        agent = SeeActAgent(grounding_strategy="text_choice_som")
        agent.taken_actions = ["Action 1", "Action 2"]
        choices = ["Choice A", "Choice B"]
        
        # Act
        prompt = agent.generate_prompt(task="Test task", choices=choices)
        
        # Assert
        assert prompt is not None
        assert isinstance(prompt, list)
        mock_query_prompt.assert_called_once()
        mock_referring_prompt.assert_called_once()

    @patch('seeact.agent.engine_factory')
    @patch('os.makedirs')
    def test_should_update_prompt_part_successfully(
        self, mock_makedirs, mock_engine_factory
    ):
        """Test that update_prompt_part updates the specified prompt section."""
        # Arrange
        mock_engine = MagicMock()
        mock_engine_factory.return_value = mock_engine
        agent = SeeActAgent()
        new_text = "Updated system prompt"
        
        # Act
        result = agent.update_prompt_part("system_prompt", new_text)
        
        # Assert
        assert result is True
        assert agent.prompts["system_prompt"] == new_text

    @patch('seeact.agent.engine_factory')
    @patch('os.makedirs')
    def test_should_return_false_when_updating_nonexistent_prompt_part(
        self, mock_makedirs, mock_engine_factory
    ):
        """Test that update_prompt_part returns False for non-existent parts."""
        # Arrange
        mock_engine = MagicMock()
        mock_engine_factory.return_value = mock_engine
        agent = SeeActAgent()
        
        # Act
        result = agent.update_prompt_part("nonexistent_part", "text")
        
        # Assert
        assert result is False


class TestSeeActAgentActionSpace:
    """Test suite for action space management."""

    @patch('seeact.agent.engine_factory')
    @patch('os.makedirs')
    def test_should_update_action_space_and_regenerate_action_format(
        self, mock_makedirs, mock_engine_factory
    ):
        """Test that update_action_space updates actions and regenerates format."""
        # Arrange
        mock_engine = MagicMock()
        mock_engine_factory.return_value = mock_engine
        agent = SeeActAgent()
        new_actions = ["CLICK", "TYPE", "SCROLL"]
        
        # Act
        agent.update_action_space(new_actions)
        
        # Assert
        assert agent.action_space == new_actions
        assert "CLICK" in agent.prompts["action_format"]
        assert "TYPE" in agent.prompts["action_format"]
        assert "SCROLL" in agent.prompts["action_format"]

    @patch('seeact.agent.engine_factory')
    @patch('os.makedirs')
    def test_should_reject_invalid_action_space_update(
        self, mock_makedirs, mock_engine_factory
    ):
        """Test that update_action_space rejects invalid input."""
        # Arrange
        mock_engine = MagicMock()
        mock_engine_factory.return_value = mock_engine
        agent = SeeActAgent()
        original_action_space = agent.action_space.copy()
        
        # Act
        agent.update_action_space("invalid")  # Not a list
        
        # Assert
        assert agent.action_space == original_action_space


class TestSeeActAgentTaskManagement:
    """Test suite for task management functionality."""

    @patch('seeact.agent.engine_factory')
    @patch('os.makedirs')
    def test_should_change_task_and_keep_action_history(
        self, mock_makedirs, mock_engine_factory
    ):
        """Test that change_task updates task without clearing history."""
        # Arrange
        mock_engine = MagicMock()
        mock_engine_factory.return_value = mock_engine
        agent = SeeActAgent(default_task="Original task")
        agent.taken_actions = ["Action 1", "Action 2"]
        
        # Act
        agent.change_task("New task", clear_history=False)
        
        # Assert
        assert agent.tasks[-1] == "New task"
        assert len(agent.taken_actions) == 3  # Original 2 + task change message
        assert "Changed task" in agent.taken_actions[-1]

    @patch('seeact.agent.engine_factory')
    @patch('os.makedirs')
    def test_should_change_task_and_clear_action_history(
        self, mock_makedirs, mock_engine_factory
    ):
        """Test that change_task clears history when requested."""
        # Arrange
        mock_engine = MagicMock()
        mock_engine_factory.return_value = mock_engine
        agent = SeeActAgent(default_task="Original task")
        agent.taken_actions = ["Action 1", "Action 2"]
        
        # Act
        agent.change_task("New task", clear_history=True)
        
        # Assert
        assert agent.tasks[-1] == "New task"
        assert len(agent.taken_actions) == 0

    @patch('seeact.agent.engine_factory')
    @patch('os.makedirs')
    def test_should_clear_action_history_successfully(
        self, mock_makedirs, mock_engine_factory
    ):
        """Test that clear_action_history removes all actions."""
        # Arrange
        mock_engine = MagicMock()
        mock_engine_factory.return_value = mock_engine
        agent = SeeActAgent()
        agent.taken_actions = ["Action 1", "Action 2", "Action 3"]
        
        # Act
        agent.clear_action_history()
        
        # Assert
        assert len(agent.taken_actions) == 0

    @patch('seeact.agent.engine_factory')
    @patch('os.makedirs')
    def test_should_reset_complete_flag(
        self, mock_makedirs, mock_engine_factory
    ):
        """Test that reset_complete_flag updates the flag correctly."""
        # Arrange
        mock_engine = MagicMock()
        mock_engine_factory.return_value = mock_engine
        agent = SeeActAgent()
        agent.complete_flag = True
        
        # Act
        agent.reset_comlete_flag(False)
        
        # Assert
        assert agent.complete_flag is False


class TestSeeActAgentFileOperations:
    """Test suite for file operations."""

    @patch('seeact.agent.engine_factory')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_should_save_action_history_to_file(
        self, mock_file, mock_makedirs, mock_engine_factory
    ):
        """Test that save_action_history writes actions to file correctly."""
        # Arrange
        mock_engine = MagicMock()
        mock_engine_factory.return_value = mock_engine
        agent = SeeActAgent()
        agent.taken_actions = ["Action 1", "Action 2", "Action 3"]
        
        # Act
        agent.save_action_history("test_history.txt")
        
        # Assert
        mock_file.assert_called()
        handle = mock_file()
        assert handle.write.call_count == 3  # One write per action


class TestSeeActAgentBrowserSession:
    """Test suite for browser session management."""

    @pytest.mark.asyncio
    @patch('seeact.agent.engine_factory')
    @patch('os.makedirs')
    @patch('seeact.agent.async_playwright')
    @patch('seeact.agent.normal_launch_async')
    @patch('seeact.agent.normal_new_context_async')
    async def test_should_initialize_browser_session_correctly(
        self, mock_new_context, mock_launch, mock_playwright, mock_makedirs, mock_engine_factory
    ):
        """Test that start() initializes browser session correctly."""
        # Arrange
        mock_engine = MagicMock()
        mock_engine_factory.return_value = mock_engine
        
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.start = AsyncMock(return_value=mock_playwright_instance)
        
        mock_browser = AsyncMock()
        mock_launch.return_value = mock_browser
        
        mock_context = AsyncMock()
        mock_context.on = MagicMock()
        mock_context.new_page = AsyncMock()
        mock_context.tracing = AsyncMock()
        mock_new_context.return_value = mock_context
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_context.new_page.return_value = mock_page
        
        agent = SeeActAgent()
        
        # Act
        await agent.start(headless=True, website="https://test.com")
        
        # Assert
        assert agent.session_control['browser'] is not None
        assert agent.session_control['context'] is not None
        mock_launch.assert_called_once()
        mock_new_context.assert_called_once()

    @pytest.mark.asyncio
    @patch('seeact.agent.engine_factory')
    @patch('os.makedirs')
    async def test_should_handle_page_close_and_switch_tabs(
        self, mock_makedirs, mock_engine_factory
    ):
        """Test that page_on_close_handler switches to available tab."""
        # Arrange
        mock_engine = MagicMock()
        mock_engine_factory.return_value = mock_engine
        
        agent = SeeActAgent()
        
        # Create mock pages
        mock_page1 = AsyncMock()
        mock_page1.title = AsyncMock(side_effect=Exception("Page closed"))
        mock_page1.url = "https://test1.com"
        
        mock_page2 = AsyncMock()
        mock_page2.title = AsyncMock(return_value="Test Page 2")
        mock_page2.url = "https://test2.com"
        mock_page2.bring_to_front = AsyncMock()
        
        mock_context = AsyncMock()
        mock_context.pages = [mock_page2]
        
        agent.session_control['context'] = mock_context
        agent._page = mock_page1
        
        # Act
        await agent.page_on_close_handler()
        
        # Assert
        assert agent.page == mock_page2
        mock_page2.bring_to_front.assert_called_once()


class TestSeeActAgentProperties:
    """Test suite for agent properties."""

    @patch('seeact.agent.engine_factory')
    @patch('os.makedirs')
    def test_should_generate_correct_screenshot_path(
        self, mock_makedirs, mock_engine_factory
    ):
        """Test that screenshot_path property generates correct path."""
        # Arrange
        mock_engine = MagicMock()
        mock_engine_factory.return_value = mock_engine
        agent = SeeActAgent()
        agent.time_step = 5
        
        # Act
        path = agent.screenshot_path
        
        # Assert
        assert "screenshots" in path
        assert "screen_5.png" in path

    @patch('seeact.agent.engine_factory')
    @patch('os.makedirs')
    def test_should_generate_correct_trace_path(
        self, mock_makedirs, mock_engine_factory
    ):
        """Test that trace_path property generates correct path."""
        # Arrange
        mock_engine = MagicMock()
        mock_engine_factory.return_value = mock_engine
        agent = SeeActAgent()
        agent.time_step = 3
        
        # Act
        path = agent.trace_path
        
        # Assert
        assert "playwright_traces" in path
        assert "3.zip" in path

    @patch('seeact.agent.engine_factory')
    @patch('os.makedirs')
    def test_should_get_and_set_page_property(
        self, mock_makedirs, mock_engine_factory
    ):
        """Test that page property getter and setter work correctly."""
        # Arrange
        mock_engine = MagicMock()
        mock_engine_factory.return_value = mock_engine
        agent = SeeActAgent()
        mock_page = MagicMock()
        agent.session_control['active_page'] = mock_page
        
        # Act
        page = agent.page
        
        # Assert
        assert page == mock_page
        
        # Test setter
        new_page = MagicMock()
        agent.page = new_page
        assert agent.page == new_page


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
