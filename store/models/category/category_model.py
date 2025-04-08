from pydantic import BaseModel, Field
from store.models.base.base_model import CreateUpdateSchema, BaseSchema, BaseAuthorSchema

class TopBooksSchema(BaseSchema):
    title: str = Field(..., examples=["The Great Gatsby"])
    author: BaseAuthorSchema = Field(..., examples=[BaseAuthorSchema(id="6683f946ec61bfa6a3c2d7c7", name="F. Scott Fitzgerald")])
    average_rating: float = Field(..., examples=[5.4])

class CategoryCreate(BaseModel):
    name: str = Field(..., examples=['Historical Fiction'])
    description: str = Field(None, examples=['Fictional stories set in the past that often incorporate real historical events'])

class CategoryCreateResponse(CreateUpdateSchema):
    name: str = Field(..., examples=['Historical Fiction'])
    description: str = Field(None, examples=['Fictional stories set in the past that often incorporate real historical events'])
    book_count: int = Field(0, examples=[12])

class CategoryUpdate(BaseModel):
    name: str = Field(None, examples=['Fiction'])
    description: str = Field(None, examples=['Updated description: Literary works created from the imagination, including novels, short stories, and plays.'])

class CategoryUpdateResponse(CreateUpdateSchema):
    name: str = Field(None, examples=['Fiction'])
    description: str = Field(None, examples=['Fiction description'])
    book_count: int = Field(0, examples=[12])

class CategorySingleResponse(CreateUpdateSchema):
    name: str = Field(None, examples=['Fiction'])
    description: str = Field(None, examples=['Fiction description'])
    book_count: int = Field(0, examples=[12])
    top_books: list[TopBooksSchema] = Field(None, examples=[
       [TopBooksSchema(id="6683f946ec61bfa6a3c2d7c7", title="The Great Gatsby", author=BaseAuthorSchema(id="6683f946ec61bfa6a3c2d7c7", name="F. Scott Fitzgerald"), average_rating=4.2)]
    ])

class CategoryResponse(CreateUpdateSchema):
    name: str = Field(None, examples=['Fiction'])
    description: str = Field(None, examples=['Fiction description'])
    book_count: int = Field(0, examples=[12])
    