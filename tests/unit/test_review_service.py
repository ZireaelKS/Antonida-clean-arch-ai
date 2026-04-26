from unittest.mock import Mock
from src.application.services import ReviewProcessingService
from src.domain.entities import SentimentScore, Review


def test_process_review_calls_analyzer():

    mock_analyzer = Mock()
    mock_analyzer.analyze.return_value = SentimentScore(label="Positive", score=0.9)

    mock_reader = Mock()

    service = ReviewProcessingService(
        analyzer=mock_analyzer,
        reader=mock_reader
    )

    result = service.analyze("Отличный сервис", "User")

    assert result.label == "Positive"
    assert result.score == 0.9

    mock_analyzer.analyze.assert_called_once()