REPORT_GENERATOR_PROMPT = """

You are a very good business analyst and a report writer.
Write a very good and comprehensive report showcasing as much data as you can based on the research data provided:-

Company Name: {name}
Research Data:
{research_data}

This should be the template you should follow to lay down the report and everything should be in a tabular format:-

**Name:**
**What they do:**
**Their USP and What makes them unique:**
**How much market they have captured or own:**
**Their biggest weakness:**
**Their biggest Strength:**
**Website:**
**Revenue and profit:**
**Pricing:**
**Conclusion:**

No more information should be included.
"""