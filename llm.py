from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from pydantic import BaseModel, Field


class FinancialMetrics(BaseModel):
    """
    Pydantic object to hold metrics
    """
    total_revenues: float = Field(..., alias="Total revenues, net of interest expense")
    net_income: float = Field(..., alias="Citigroup's net income")
    book_value_per_share: float = Field(..., alias="Book value per share")
    tangible_book_value_per_share: float = Field(..., alias="Tangible book value per share")
    cet1_capital_ratio: float = Field(..., alias="Common Equity Tier 1 Capital ratio")

    class Config:
        # Allow aliasing of field names
        allow_population_by_field_name = True


class QuarterlyMetrics(BaseModel):
    """
    Pydantic object to hold Quarters metrics
    """
    Q2_24: FinancialMetrics = Field(..., alias="Q2'24")
    Q3_24: FinancialMetrics = Field(..., alias="Q3'24")


def extract_llm(file_content):
    """
    Using file content to extract metrics using structure output wrapper
    :param file_content: excel/pdf content
    :return: quarters with metrics as dict
    """
    prompt_template = """
    Given the following content extracted from a PDF/Excel file, your job is to extract the following metrics for Q2'24 and Q3'24:
    Total revenues, net of interest expense, 
    Citigroup's net income,
    Book value per share,
    Tangible book value per share,
    Common Equity Tier 1 (CET1) Capital ratio
    
    Content: {file_content}
    """

    # declare prompt template
    prompt = PromptTemplate(input_variables=["file_content"], template=prompt_template)

    # setting llm model
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
    # setting langchain chain
    llm_chain = LLMChain(prompt=prompt, llm=llm)

    # wrapping as structure output
    structured_llm = llm_chain.llm.with_structured_output(QuarterlyMetrics)

    # Generate the response with updated structure
    response = structured_llm.invoke(prompt.format(file_content=file_content))
    return response.dict(by_alias=True)

