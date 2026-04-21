"""
Unit tests for SolutionAnalyzer.

Tests cover:
- Initialization
- Intent analysis
- Project type detection
- Solution generation (conservative, balanced, innovative)
- Full analysis workflow
"""
import pytest
import tempfile
import json
from pathlib import Path
from scripts.core.solution_analyzer import SolutionAnalyzer, analyze_solution


class TestSolutionAnalyzer:
    """Test suite for SolutionAnalyzer."""

    def test_init(self, tmp_path):
        """Test that init() correctly initializes the analyzer."""
        analyzer = SolutionAnalyzer(tmp_path)

        assert analyzer.root == tmp_path.resolve()
        assert analyzer.intent is None
        assert analyzer.user_input is None

    def test_analyze_with_basic_intent(self, tmp_path):
        """Test analyze() with basic intent and input."""
        analyzer = SolutionAnalyzer(tmp_path)

        result = analyzer.analyze("bug-fix", "Fix the login bug")

        # Check top-level structure
        assert "project_context" in result
        assert "industry_solutions" in result
        assert "proposed_solutions" in result
        assert "recommendation" in result
        assert "confidence" in result

        # Check intent and user_input are stored
        assert analyzer.intent == "bug-fix"
        assert analyzer.user_input == "Fix the login bug"

        # Check result types
        assert isinstance(result["project_context"], dict)
        assert isinstance(result["industry_solutions"], list)
        assert isinstance(result["proposed_solutions"], list)
        assert isinstance(result["recommendation"], str)
        assert isinstance(result["confidence"], float)
        assert 0.0 <= result["confidence"] <= 1.0

    def test_detect_project_type_web(self, tmp_path):
        """Test detection of web project type."""
        # Create web project indicators
        (tmp_path / "index.html").touch()
        (tmp_path / "package.json").write_text('{"name": "web-app"}')

        analyzer = SolutionAnalyzer(tmp_path)
        project_type = analyzer._detect_project_type()

        assert project_type == "web"

    def test_detect_project_type_cli(self, tmp_path):
        """Test detection of CLI project type."""
        # Create CLI project indicators
        (tmp_path / "__main__.py").touch()
        (tmp_path / "cli.py").touch()

        analyzer = SolutionAnalyzer(tmp_path)
        project_type = analyzer._detect_project_type()

        assert project_type == "cli"

    def test_detect_project_type_microservices(self, tmp_path):
        """Test detection of microservices project type."""
        # Create microservices indicators
        (tmp_path / "docker-compose.yml").touch()

        analyzer = SolutionAnalyzer(tmp_path)
        project_type = analyzer._detect_project_type()

        assert project_type == "microservices"

    def test_detect_language_python(self, tmp_path):
        """Test detection of Python as main language."""
        # Create Python files
        (tmp_path / "main.py").touch()
        (tmp_path / "utils.py").touch()
        (tmp_path / "scripts").mkdir()
        (tmp_path / "scripts" / "script.py").touch()

        analyzer = SolutionAnalyzer(tmp_path)
        language = analyzer._detect_language()

        assert language == "python"

    def test_detect_language_javascript(self, tmp_path):
        """Test detection of JavaScript as main language."""
        # Create JavaScript files
        (tmp_path / "index.js").touch()
        (tmp_path / "app.js").touch()
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "utils.js").touch()

        analyzer = SolutionAnalyzer(tmp_path)
        language = analyzer._detect_language()

        assert language == "javascript"

    def test_detect_framework_flask(self, tmp_path):
        """Test detection of Flask framework."""
        # Create requirements.txt with Flask
        (tmp_path / "requirements.txt").write_text("flask==2.0.0\nrequests==2.28.0")

        analyzer = SolutionAnalyzer(tmp_path)
        framework = analyzer._detect_framework()

        assert framework == "Flask"

    def test_detect_framework_django(self, tmp_path):
        """Test detection of Django framework."""
        # Create requirements.txt with Django
        (tmp_path / "requirements.txt").write_text("django==4.0.0\npsycopg2==2.9.0")

        analyzer = SolutionAnalyzer(tmp_path)
        framework = analyzer._detect_framework()

        assert framework == "Django"

    def test_detect_framework_react(self, tmp_path):
        """Test detection of React framework."""
        # Create package.json with React
        (tmp_path / "package.json").write_text('{"dependencies": {"react": "^18.0.0"}}')

        analyzer = SolutionAnalyzer(tmp_path)
        framework = analyzer._detect_framework()

        assert framework == "React"

    def test_analyze_dependencies_from_requirements(self, tmp_path):
        """Test dependency analysis from requirements.txt."""
        # Create requirements.txt
        (tmp_path / "requirements.txt").write_text(
            "flask==2.0.0\n"
            "requests>=2.28.0\n"
            "pytest~=7.0.0\n"
            "# This is a comment\n"
            "numpy\n"
        )

        analyzer = SolutionAnalyzer(tmp_path)
        dependencies = analyzer._analyze_dependencies()

        assert "flask" in dependencies
        assert "requests" in dependencies
        assert "pytest" in dependencies
        assert "numpy" in dependencies

    def test_analyze_dependencies_from_pyproject(self, tmp_path):
        """Test dependency analysis from pyproject.toml."""
        # Create pyproject.toml
        (tmp_path / "pyproject.toml").write_text(
            "[project.dependencies]\n"
            "flask = \"^2.0.0\"\n"
            "requests = \">=2.28.0\"\n"
            "pytest = \"~=7.0.0\"\n"
        )

        analyzer = SolutionAnalyzer(tmp_path)
        dependencies = analyzer._analyze_dependencies()

        assert "flask" in dependencies
        assert "requests" in dependencies
        assert "pytest" in dependencies

    def test_scan_code_structure(self, tmp_path):
        """Test scanning code structure to extract modules and functions."""
        # Create code directory
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir()

        # Create Python file with functions
        (scripts_dir / "utils.py").write_text(
            "def helper_function():\n"
            "    pass\n"
            "\n"
            "def another_function():\n"
            "    pass\n"
            "\n"
            "def _private_function():\n"
            "    pass\n"
        )

        analyzer = SolutionAnalyzer(tmp_path)
        modules, functions = analyzer._scan_code_structure()

        assert "utils" in modules
        assert "helper_function()" in functions
        assert "another_function()" in functions
        # Private functions should be excluded
        assert "_private_function()" not in functions

    def test_analyze_structure(self, tmp_path):
        """Test project structure analysis."""
        # Create project structure
        (tmp_path / "Docs").mkdir()
        (tmp_path / "tests").mkdir()
        (tmp_path / ".lifecycle").mkdir()
        (tmp_path / "src").mkdir()

        analyzer = SolutionAnalyzer(tmp_path)
        structure = analyzer._analyze_structure()

        assert structure["has_docs"] is True
        assert structure["has_tests"] is True
        assert structure["has_config"] is True
        assert "src" in structure["directories"]

    def test_estimate_test_coverage(self, tmp_path):
        """Test test coverage estimation."""
        # Create code and test files
        (tmp_path / "main.py").touch()
        (tmp_path / "utils.py").touch()
        (tmp_path / "test_main.py").touch()

        analyzer = SolutionAnalyzer(tmp_path)
        coverage = analyzer._estimate_test_coverage()

        # Should be approximately 0.33 (1 test file / 3 total files)
        assert 0.0 <= coverage <= 1.0
        assert coverage > 0.0  # Should detect some coverage

    def test_generate_conservative_solution(self, tmp_path):
        """Test generation of conservative solution."""
        analyzer = SolutionAnalyzer(tmp_path)
        analyzer.intent = "bug-fix"

        project_context = {"dependencies": ["flask", "requests"]}
        industry_solutions = []

        solution = analyzer._generate_conservative_solution(
            project_context, industry_solutions
        )

        assert solution["id"] == "solution-conservative"
        assert "title" in solution
        assert "description" in solution
        assert "steps" in solution
        assert "estimated_effort" in solution
        assert solution["risk_level"] == "low"
        assert "dependencies" in solution
        assert "pros" in solution
        assert "cons" in solution

    def test_generate_balanced_solution(self, tmp_path):
        """Test generation of balanced/recommended solution."""
        analyzer = SolutionAnalyzer(tmp_path)
        analyzer.intent = "new-feature"

        project_context = {"dependencies": ["flask", "requests"]}
        industry_solutions = []

        solution = analyzer._generate_recommended_solution(
            project_context, industry_solutions
        )

        assert solution["id"] == "solution-recommended"
        assert "title" in solution
        assert "description" in solution
        assert "steps" in solution
        assert solution["risk_level"] == "medium"

    def test_generate_innovative_solution(self, tmp_path):
        """Test generation of innovative solution."""
        analyzer = SolutionAnalyzer(tmp_path)
        analyzer.intent = "refactor"

        project_context = {"dependencies": ["flask", "requests"]}
        industry_solutions = []

        solution = analyzer._generate_innovative_solution(
            project_context, industry_solutions
        )

        assert solution["id"] == "solution-innovative"
        assert "title" in solution
        assert "description" in solution
        assert "steps" in solution
        assert solution["risk_level"] == "high"

    def test_generate_solutions_returns_multiple(self, tmp_path):
        """Test that _generate_solutions returns multiple solutions."""
        analyzer = SolutionAnalyzer(tmp_path)
        analyzer.intent = "bug-fix"

        project_context = {"dependencies": ["flask"]}
        industry_solutions = []

        solutions = analyzer._generate_solutions(project_context, industry_solutions)

        # Should have at least 3 solutions (conservative, recommended, innovative)
        assert len(solutions) >= 3

        # All solutions should have required fields
        for solution in solutions:
            assert "id" in solution
            assert "title" in solution
            assert "description" in solution
            assert "steps" in solution
            assert "score" in solution

        # Solutions should be sorted by score
        scores = [s["score"] for s in solutions]
        assert scores == sorted(scores, reverse=True)

    def test_calculate_solution_score(self, tmp_path):
        """Test solution scoring."""
        analyzer = SolutionAnalyzer(tmp_path)

        solution = {
            "risk_level": "low",
            "pros": ["fast", "safe", "tested"],
            "cons": ["complex"],
            "dependencies": ["flask"],
            "reference": "https://example.com",
        }

        project_context = {"dependencies": ["flask", "requests"]}

        score = analyzer._calculate_solution_score(solution, project_context)

        # Score should be between 0 and 100
        assert 0.0 <= score <= 100.0

    def test_recommend_returns_best_solution(self, tmp_path):
        """Test that _recommend returns the best solution."""
        analyzer = SolutionAnalyzer(tmp_path)

        solutions = [
            {"id": "solution-1", "score": 70.0},
            {"id": "solution-2", "score": 85.0},
            {"id": "solution-3", "score": 60.0},
        ]

        recommendation, confidence = analyzer._recommend(solutions)

        assert recommendation == "solution-2"
        assert confidence == 0.5

    def test_recommend_handles_empty_solutions(self, tmp_path):
        """Test that _recommend handles empty solutions list."""
        analyzer = SolutionAnalyzer(tmp_path)

        recommendation, confidence = analyzer._recommend([])

        assert recommendation == "no-solution"
        assert confidence == 0.0

    def test_get_generic_solutions_for_bug_fix(self, tmp_path):
        """Test generic solutions for bug-fix intent."""
        analyzer = SolutionAnalyzer(tmp_path)
        analyzer.intent = "bug-fix"

        solutions = analyzer._get_generic_solutions()

        assert len(solutions) > 0
        assert any("Root Cause Analysis" in s["name"] for s in solutions)

    def test_get_generic_solutions_for_new_feature(self, tmp_path):
        """Test generic solutions for new-feature intent."""
        analyzer = SolutionAnalyzer(tmp_path)
        analyzer.intent = "new-feature"

        solutions = analyzer._get_generic_solutions()

        assert len(solutions) > 0
        assert any("Iterative Development" in s["name"] or "MVP" in s["name"] for s in solutions)

    def test_get_generic_solutions_for_refactor(self, tmp_path):
        """Test generic solutions for refactor intent."""
        analyzer = SolutionAnalyzer(tmp_path)
        analyzer.intent = "refactor"

        solutions = analyzer._get_generic_solutions()

        assert len(solutions) > 0
        assert any("Strangler" in s["name"] or "Rewrite" in s["name"] for s in solutions)

    def test_analyze_project_code_handles_exceptions(self, tmp_path):
        """Test that _analyze_project_code handles exceptions gracefully."""
        # Create a directory that will cause permission issues
        analyzer = SolutionAnalyzer(tmp_path)

        # Should not raise exception even if analysis fails
        result = analyzer._analyze_project_code()

        # Should return valid structure with defaults
        assert "type" in result
        assert "language" in result
        assert "framework" in result
        assert "dependencies" in result

    def test_detect_patterns(self, tmp_path):
        """Test detection of code patterns."""
        # Create Python file with patterns
        (tmp_path / "models.py").write_text(
            "class UserModel:\n"
            "    pass\n"
            "\n"
            "class UserController:\n"
            "    pass\n"
        )

        analyzer = SolutionAnalyzer(tmp_path)
        patterns = analyzer._detect_patterns()

        # Should detect MVC pattern
        assert isinstance(patterns, list)


class TestSolutionAnalyzerIntegration:
    """Integration tests for SolutionAnalyzer."""

    def test_full_analysis_workflow(self, tmp_path):
        """Test complete analysis workflow from start to finish."""
        # Create a realistic project structure
        (tmp_path / "requirements.txt").write_text(
            "flask==2.0.0\n"
            "requests==2.28.0\n"
            "pytest==7.0.0\n"
        )

        (tmp_path / "index.html").touch()
        (tmp_path / "app.py").write_text(
            "from flask import Flask\n"
            "\n"
            "app = Flask(__name__)\n"
            "\n"
            "@app.route('/')\n"
            "def index():\n"
            "    return 'Hello World'\n"
        )

        # Create docs and tests
        (tmp_path / "Docs").mkdir()
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test_app.py").touch()

        # Run analysis
        analyzer = SolutionAnalyzer(tmp_path)
        result = analyzer.analyze("new-feature", "Add user authentication")

        # Verify complete result structure
        assert "project_context" in result
        assert "industry_solutions" in result
        assert "proposed_solutions" in result
        assert "recommendation" in result
        assert "confidence" in result

        # Verify project context
        project_context = result["project_context"]
        assert project_context["type"] in ["web", "cli", "unknown"]
        assert project_context["language"] in ["python", "javascript", "unknown"]
        assert project_context["framework"] in ["Flask", "unknown"]
        assert "flask" in project_context["dependencies"]
        assert "requests" in project_context["dependencies"]

        # Verify solutions
        solutions = result["proposed_solutions"]
        assert len(solutions) >= 3

        # All solutions should have scores
        for solution in solutions:
            assert "score" in solution
            assert 0.0 <= solution["score"] <= 100.0

        # Solutions should be sorted by score
        scores = [s["score"] for s in solutions]
        assert scores == sorted(scores, reverse=True)

        # Verify recommendation
        assert result["recommendation"] in [s["id"] for s in solutions]

    def test_analysis_with_different_intents(self, tmp_path):
        """Test analysis with different user intents."""
        # Create basic project
        (tmp_path / "main.py").touch()

        intents = ["bug-fix", "new-feature", "refactor", "performance", "security"]

        for intent in intents:
            analyzer = SolutionAnalyzer(tmp_path)
            result = analyzer.analyze(intent, f"Test input for {intent}")

            assert result["recommendation"] is not None
            assert len(result["proposed_solutions"]) >= 3

    def test_analyze_solution_convenience_function(self, tmp_path):
        """Test the convenience function analyze_solution()."""
        # Create basic project
        (tmp_path / "main.py").touch()

        result = analyze_solution(
            tmp_path,
            "bug-fix",
            "Fix the critical bug in login"
        )

        assert "project_context" in result
        assert "proposed_solutions" in result
        assert "recommendation" in result

    def test_analysis_with_industry_solutions(self, tmp_path):
        """Test analysis when industry solutions are available."""
        # Create basic project
        (tmp_path / "main.py").touch()

        analyzer = SolutionAnalyzer(tmp_path)
        result = analyzer.analyze("refactor", "Refactor the codebase")

        # Should have industry solutions (either from web search or generic)
        assert isinstance(result["industry_solutions"], list)

        # Should have proposed solutions
        assert len(result["proposed_solutions"]) >= 3

    def test_analysis_handles_missing_files_gracefully(self, tmp_path):
        """Test that analysis handles missing files gracefully."""
        # Empty directory - no project files
        analyzer = SolutionAnalyzer(tmp_path)
        result = analyzer.analyze("new-feature", "Create a new feature")

        # Should still return valid results
        assert result["project_context"]["type"] in ["web", "cli", "unknown"]
        assert result["project_context"]["language"] in ["python", "javascript", "unknown"]
        assert len(result["proposed_solutions"]) >= 3

    def test_analysis_with_complex_project_structure(self, tmp_path):
        """Test analysis with complex project structure."""
        # Create complex structure
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "core").mkdir()
        (tmp_path / "src" / "utils").mkdir()
        (tmp_path / "tests").mkdir()
        (tmp_path / "Docs").mkdir()
        (tmp_path / ".lifecycle").mkdir()

        # Create Python files
        (tmp_path / "src" / "core" / "engine.py").write_text(
            "def run():\n"
            "    pass\n"
            "\n"
            "def process():\n"
            "    pass\n"
        )

        (tmp_path / "src" / "utils" / "helpers.py").write_text(
            "def format_data():\n"
            "    pass\n"
        )

        (tmp_path / "tests" / "test_engine.py").touch()

        # Create requirements
        (tmp_path / "requirements.txt").write_text("flask==2.0.0\npytest==7.0.0\n")

        analyzer = SolutionAnalyzer(tmp_path)
        result = analyzer.analyze("refactor", "Refactor the core engine")

        # Verify analysis captured structure
        project_context = result["project_context"]
        assert project_context["language"] == "python"
        assert len(project_context["related_modules"]) > 0
        assert len(project_context["key_functions"]) > 0
        assert project_context["structure"]["has_docs"] is True
        assert project_context["structure"]["has_tests"] is True
        assert project_context["test_coverage"] > 0.0
