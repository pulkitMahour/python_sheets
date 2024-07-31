from datetime import datetime as dt
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time
import os
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate

class Solver(BaseModel):
  problem:str = Field(description="Give an overview on the problem. Divide the problem into smaller, more manageable parts")
  solution:str = Field(description="Brainstorm potential solutions and approaches. Don't limit yourself to conventional ideas; explore unconventional possibilities")
  analyze:str = Field(description="Analyze the feasibility, effectiveness, and potential consequences of each solution. Consider factors like cost, time, resources, and risks.")
  selection:str = Field(description="Select the most promising solution based on your evaluation")


def addata():
    st.subheader("Task Management Portal", divider="violet")
    st.markdown("Enter the details of the new task below")

    if "situat" not in st.session_state:
        st.session_state.situat = False

    if "t_height" not in st.session_state:
        st.session_state.t_height = 20

    def response_generator(query):
        api_key = os.environ['API_KEY']
        model = GoogleGenerativeAI(model="models/gemini-1.5-flash", google_api_key=api_key, temperature=0.7)

        prompt = f"how to achive this task, give some instructions'{query}'"

        # parser = PydanticOutputParser(pydantic_object=Solver)
        # prompt = PromptTemplate(
        #     template="Answer the user query.\n{format_instructions}\n{query}\n",
        #     input_variables=["query"],
        #     partial_variables={
        #         "format_instructions": parser.get_format_instructions()
        #     },
        # )
        # chain = prompt | model | parser
        # response = chain.invoke({"query": query})
        response = model.invoke(prompt)

        st.session_state.additnl_info = response
        # print(type(response), response)
        st.session_state.t_height = response.count("\n") * 30
        current_text = ""
        for char in response:
            current_text += char
            yield current_text
            time.sleep(0.01)

    with st.container(border=True):

        if st.session_state.situat:
            st.session_state.task_info = ""
            st.session_state.situat = False
            
        task = st.text_input(label="Task*", key="task_info")
        additional_info = st.empty()

        # add additional info in the text area and show a spinner
        with st.spinner("generating..."):
            generate = st.button(label="🐲 Generate with AI", disabled=not st.session_state.task_info or st.session_state.task_info.isspace())

            if generate:
                gen_text = response_generator(st.session_state.task_info)
                for i in gen_text:
                    additional_info.text_area(label="Additional information 2", value=i, height=st.session_state.t_height)

        deadline = st.date_input("Deadline", help="If you don’t choose a deadline, it will be set by default to one week.", format="DD-MM-YYYY", min_value=dt.now(), value=None)

        add_task = st.button(label="Add Task")
        now = dt.now()

        #Adding a task to the Spread sheet
        if add_task:
            if not st.session_state.task_info or st.session_state.task_info.isspace():
                st.toast(':red[Task name is required]')
            else:
                additional_info.text_area(label="Additional information", value=st.session_state.additnl_info, height=st.session_state.t_height)
                if not deadline:
                    deadline = now + pd.DateOffset(weeks=1)

                # Connect to Google Sheets and update the spreadsheet with the new task details.
                conn = st.connection("gsheets", type=GSheetsConnection)
                existing_data = conn.read(worksheet="Sheet1", usecols=list(range(5)), ttl=5)
                existing_data = existing_data.dropna(how="all")

                task_data = pd.DataFrame(
                    [
                        {
                            "Task No.": len(existing_data)+1,
                            "Title": st.session_state.task_info,
                            "Instructions / Comments": st.session_state.additnl_info,
                            "Assigned Date": now.strftime("%a %d %B, %Y"),
                            "Estimated End Date": deadline.strftime("%a %d %B, %Y")
                        }
                    ]
                )
            
                updated_df = pd.concat([existing_data, task_data], ignore_index=True)
                conn.update(worksheet="Sheet1", data=updated_df)

                # Fetch the updated data from the spreadsheet to display the latest task details.
                new_data = conn.read(worksheet="Sheet1", usecols=list(range(6)), ttl=5)
                new_data = new_data.iloc[-1]

                st.session_state.situat = True
                st.session_state.additnl_info = ""
                st.toast(":green[Task details successfully submitted]")
                rmvr = st.caption(":orange[The task has been added successfully. And this preview will dissappear in the next 10 seconds]")
                lst_col = st.dataframe(new_data, use_container_width=True)

                # Clear the session state and rerun the app to update the UI.
                time.sleep(10)
                lst_col.empty()
                rmvr.empty()
                st.session_state.t_height = 20
                st.rerun()
                
        additional_info.text_area(label="Additional information", key="additnl_info", height=st.session_state.t_height)
    
    
