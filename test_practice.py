import pytest
from practice import open_pdf, get_page_count, \
    get_text_from_page, close_pdf
from unittest.mock import Mock, patch, MagicMock

# Test with mocking (no real PDF needed)
class TestPDFFunctions:

    @patch('practice.fitz.open')
    def test_open_pdf(self, mock_fitz_open):       
        """Test that open_pdf calls fitz.open correctly"""
        mock_pdf = Mock()
        mock_fitz_open.return_value = mock_pdf     

        result = open_pdf("dummy.pdf")

        mock_fitz_open.assert_called_once_with("dummy.pdf")
        assert result == mock_pdf

    def test_get_page_count(self):
        """Test page count returns correct length"""
        mock_pdf = MagicMock()
        mock_pdf.__len__.return_value = 5

        result = get_page_count(mock_pdf)

        assert result == 5

    def test_get_text_from_page(self):
        """Test text extraction from a page"""     
        mock_pdf = MagicMock()
        mock_page = Mock()
        mock_page.get_text.return_value ="Sample text"
        mock_pdf.__getitem__.return_value =mock_page

        result = get_text_from_page(mock_pdf,0)

        assert result == "Sample text" 
        mock_pdf.__getitem__.assert_called_once_with(0)    
        mock_page.get_text.assert_called_once()    

    def test_close_pdf(self):
        """Test that close is called on pdf object"""
        mock_pdf = Mock()

        close_pdf(mock_pdf)

        mock_pdf.close.assert_called_once()        

# Integration test with a real PDF (optional)      
@pytest.mark.integration
def test_full_workflow_with_real_pdf():
    """Test with an actual PDF file if
available"""
    # Create a simple test PDF or use existing one
    test_pdf_path = "test.pdf"  # You'd need a test PDF

    try:
        pdf = open_pdf(test_pdf_path)
        assert pdf is not None

        count = get_page_count(pdf)
        assert count >= 0

        if count > 0:
            text = get_text_from_page(pdf, 0)      
            assert isinstance(text, str)

        close_pdf(pdf)
    except FileNotFoundError:
        pytest.skip("Test PDF not found")
