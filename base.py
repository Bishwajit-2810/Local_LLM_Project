from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

template = """
Answer the question below.

Here is the conversation history: {context}

Question: {question}

Answer: 
"""

model = OllamaLLM(model="llama3.2")
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model



def handle_conversation():
    context=""
    print("welcome to AI ChatBot! Type 'exit' to quit.")
    while True:
        user_input=input("You: ")
        if user_input.lower() == "exit":
            print("Good Bye")
            break
        result= chain.invoke({"context": context,"question":user_input})
        print("AI: ",result)
        context+=f'\nUser: {user_input}\nAI: {result}'
        

handle_conversation()



