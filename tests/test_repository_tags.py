import unittest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from src.schemas.tags_schema import TagModel, TagResponse
from src.database.models import Tag
from src.repository.tags import (
    get_tags,
    get_tag_by_id,   
    get_tag_by_tagname,
    update_tag,
    remove_tag,
    retrieve_tags_for_picture
)

class TestNotes(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = AsyncMock(spec=AsyncSession)
        self.mock_tag = self._create_mock_tag()
        self.mock_tag_response = self._create_tag_response
        
    def tearDown(self):
        del self.session
        
    def _create_mock_tag(self):
        tag = Tag()
        tag.id = 1
        tag.tagname = "alex"
        return tag
    
    def _create_tag_response(self):
        tag_response = TagResponse()
        tag_response.id=1,
        tag_response.tagname="alex",
        tag_response.created_at=datetime.time,
        tag_response.updated_at=datetime.time
        
    async def test_get_tags(self):
        self.session.execute.return_value = MagicMock(scalar=MagicMock(return_value=self.mock_tag))
        result = await get_tags(db=self.session)
        self.assertTrue(result)
        
    async def test_get_tag_by_id(self):
        self.session.execute.return_value = MagicMock(scalar=MagicMock(return_value=self.mock_tag))
        result = await get_tag_by_id(tag_id=self._create_mock_tag().id, db=self.session)
        self.assertEqual(result.id, self._create_mock_tag().id)
        
    async def test_get_tag_by_tagname(self):
        self.session.execute.return_value = MagicMock(scalar=MagicMock(return_value=self.mock_tag))
        result = await get_tag_by_tagname(tagname=self._create_mock_tag().tagname, db=self.session)
        self.assertEqual(result.tagname, self._create_mock_tag().tagname)

    async def test_update_tag(self):
        body = TagModel(tagname='test')
        self.session.execute.return_value = MagicMock(scalar=MagicMock(return_value=self.mock_tag_response))
        result = await update_tag(tag_id=self._create_mock_tag().id, body=body, db=self.session)
        # self.assertEqual(result.tagname, self._create_mock_tag().tagname)


if __name__ == "__main__":
    unittest.main()           
        