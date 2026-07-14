INTENT_DETECTION_PROMPT = """

You are an assistant whose task is to see the user query:-

{user_input}

And then decide whether the given query is about:-

1. Idea of a Product/Project/SaaS proposed by the user:- return "idea"
2. Company Description/Profile provided by the user:- return "company"
3. Product/Project/SaaS Description provided by the user:- return "product"

Return only one word only.

"""

CONTEXT_RETRIEVAL_PROMPT = """

You are an assistant whose task is to ask 3 questions which you should search on internet to get the proper information about:-

User Input:- {user_input}
For the intent to get information on:- {user_intent} provided

If its an "idea", then ask questions to get most information to validate the idea and look for similar products description for more information.
If its a "company", then ask questions to get most information on similar working pattern and also how such companies work.
If its a "product", then ask questions to get most information about the product and also how it works.

Return only 3 questions in a list format.

Example:- ["question1", "question2", "question3"]

"""