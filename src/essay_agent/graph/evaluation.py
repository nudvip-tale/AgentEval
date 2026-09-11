import json
from agentevals.trajectory.match import create_trajectory_match_evaluator
from src.essay_agent.graph.run_graph import run_multi_agent_workflow_silent
from langchain_core.messages import convert_to_openai_messages

# def evaluate_tool_usage(user_message: str):
#     """Evaluate tool usage against expected tools"""
    
#     # Run the workflow and get results
#     chunks = run_multi_agent_workflow_silent(user_message)
    
#     # Extract messages from chunks (same logic as in main.py)
#     all_messages = []
    
#     for chunk in chunks:
#         for key, value in chunk.items():
#             if key in ['supervisor', 'work_agent', 'review_agent'] and isinstance(value, dict):
#                 # Extract messages from agent responses
#                 if 'messages' in value and isinstance(value['messages'], list):
#                     all_messages.extend(value['messages'])
#             elif key == 'messages' and isinstance(value, list):
#                 # Direct messages in chunk
#                 all_messages.extend(value)
    
#     # Convert to OpenAI format
#     outputs = []
#     if all_messages:
#         try:
#             outputs = convert_to_openai_messages(all_messages)
#         except Exception as e:
#             print(f"Error converting to OpenAI format: {e}")
#             # Fallback: manual conversion
#             for msg in all_messages:
#                 try:
#                     if hasattr(msg, 'type'):
#                         role_mapping = {
#                             'human': 'user',
#                             'ai': 'assistant',
#                             'system': 'system',
#                             'tool': 'tool'
#                         }
#                         role = role_mapping.get(msg.type, 'user')
#                         content = getattr(msg, 'content', str(msg))
                        
#                         openai_msg = {'role': role, 'content': content}
                        
#                         # Handle tool calls if present
#                         if hasattr(msg, 'tool_calls') and msg.tool_calls:
#                             openai_msg['tool_calls'] = msg.tool_calls
                        
#                         # Handle tool call id if present
#                         if hasattr(msg, 'tool_call_id') and msg.tool_call_id:
#                             openai_msg['tool_call_id'] = msg.tool_call_id
                            
#                         outputs.append(openai_msg)
                        
#                 except Exception as msg_error:
#                     print(f"Error processing message: {msg_error}")
#                     continue
    
    
#     # Create reference outputs with expected tools
#     reference_outputs = [
#   {
#     "role": "user",
#     "content": "tell top 5 news articles on trump, then review the summary for accuracy and coherence."
#   },
#   {
#     "role": "assistant",
#     "name": "supervisor",
#     "tool_calls": [
#       {
#         "type": "function",
#         "id": "call_oc1VePz8lLrAPueDiDZQi13e",
#         "function": {
#           "name": "transfer_to_work_agent",
#           "arguments": "{}"
#         }
#       }
#     ],
#     "content": ""
#   },
#   {
#     "role": "tool",
#     "name": "transfer_to_work_agent",
#     "tool_call_id": "call_oc1VePz8lLrAPueDiDZQi13e",
#     "content": "Successfully transferred to work_agent"
#   },
#   {
#     "role": "assistant",
#     "name": "work_agent",
#     "tool_calls": [
#       {
#         "type": "function",
#         "id": "call_XkOk5zoX9ZDuQFH8XkFXjfKo",
#         "function": {
#           "name": "get_related_news_tool",
#           "arguments": "{\"topic\": \"Trump\"}"
#         }
#       }
#     ],
#     "content": ""
#   },
#   {
#     "role": "tool",
#     "name": "get_related_news_tool",
#     "tool_call_id": "call_XkOk5zoX9ZDuQFH8XkFXjfKo",
#     "content": "[{'title': 'Governor Newsom suing President Trump and Department of Defense for illegal takeover of CalGuard unit', 'content': None, 'date': '9 days ago', 'datetime': '2025-06-09T04:12:38.986450', 'link': 'https://www.gov.ca.gov/2025/06/09/governor-newsom-suing-president-trump-and-department-of-defense-for-illegal-takeover-of-calguard-unit/', 'source': 'Governor of California (.gov)', 'reporter': [None], 'cos_sim': 0.23444709399418337}, {'title': 'I have formally requested the Trump Administration rescind their unlawful deployment of troops in Los Angeles county and return them to my command. We didn\u2019t have a problem until Trump got involved. This is a serious breach of state sovereignty \u2014 inflamin', 'content': 'JavaScript is not available.\\n\\nWe\u2019ve detected that JavaScript is disabled in this browser. Please enable JavaScript or switch to a supported browser to continue using x.com. You can see a list of supported browsers in our Help Center.\\n\\nHelp Center', 'date': '10 days ago', 'datetime': '2025-06-08T04:12:38.987377', 'link': 'https://x.com/GavinNewsom/status/1931840646773715068', 'source': 'x.com', 'reporter': [None], 'cos_sim': 0.26527195374702317}, {'title': \"Trump says Musk will face 'serious consequences' if he funds Democratic candidates\", 'content': '\u201cIf he does, he\u2019ll have to pay the consequences for that,\u201d Trump told NBC News in a phone interview, but declined to share what those consequences would be.\\n\\nElon Musk listens as Donald Trump speaks in the Oval Office of the White House on Feb. 11, 2025. Jim Watson / AFP - Getty Images file\\n\\n...\\n\\nThe vice president also called it a \u201chuge mistake\u201d for Musk to target the president over his frustrations with the House version of the bill, saying, \u201cThe process in D.C., if you\u2019re a business leader, you probably get frustrated with that process because it\u2019s more, you know, bureaucratic, it\u2019s more slow moving.\"\\n\\nHe added, \"I think there\u2019s just some frustrations there. But I really, man, I think it\u2019s a huge mistake for him to go after the president like that.\u201d', 'date': '11 days ago', 'datetime': '2025-06-07T04:12:38.988214', 'link': 'https://www.nbcnews.com/politics/donald-trump/trump-elon-musk-consequences-funds-democratic-candidates-rcna211605', 'source': 'NBC News', 'reporter': ['Kristen Welker', 'Alexandra Marquez'], 'cos_sim': 0.40238817782498104}, {'title': \"From Day One, Trump's Immigration Agenda Has Grown More Extreme\", 'content': \"Mahmoud Khalil Renews Request for Immediate Release from Illegitimate ICE Detention\\n\\nNEWARK, N.J. \u2013 Mahmoud Khalil\u2019s legal team wrote the court today asking for his immediate release on bail, or, at a minimum, to order his return to New Jersey. The request comes after the government informed the court Friday that it would continue to detain Mr. Khalil in a remote facility in Jena, Louisiana, based on false and pretextual allegations connected with his green card application because a preliminary injunction that entered into effect Friday blocks his detention on purported foreign policy grounds. The federal judge overseeing his case, Michael E. Farbiarz, wrote Friday that, even though the government virtually never detains anyone on such \u201cmisrepresentation\u201d charges, the court would not, at this point, prohibit the government from relying upon such pretextual and retaliatory allegations to continue Mr. Khalil\u2019s detention. \u201cThe government is making desperate, last ditch attempts to keep my husband unjustly imprisoned,\u201d said Dr. Noor Abdalla, Mahmoud Khalil\u2019s wife. \u201cWe are not afraid and will not be intimidated, because we know, and the government knows, it is only a matter of time before Mahmoud is free. The American people are with us, and can see right through the government\u2019s unjust attempts to delay his release. No matter what the government pulls, we will bring Mahmoud home safe.\u201d \u201cBecause its outrageous attempt to detain Mahmoud based only on Secretary Rubio\u2019s say-so has been struck down as unconstitutional, the government now stoops to a new low by doing what the federal court said the government virtually never does\u2014detaining a U.S. permanent resident based on an alleged omission in an immigration application,\u201d said Ramzi Kassem, co-director of CLEAR, at CUNY School of Law. \u201cThis only further proves Mahmoud\u2019s claim that the government is retaliating against him for exercising his right to speak in defense of Palestinian rights and we won\u2019t stop until he is free.\u201d \u201cLike it has for the past three months, the government is using all of the tools available to it to hinder justice for Mahmoud,\u201d said Brett Max Kaufman, senior counsel in the ACLU\u2019s Center for Democracy. \u201cThe government practically never holds people in detention on a charge like this, and it\u2019s clear that the government is doing anything they can to punish Mahmoud for his speech about Palestine. We will not stop until he\u2019s home with his family.\u201d Today\u2019s filing notes that Mr. Khalil is neither a flight risk nor a danger to anyone. It further explains that the court previously recognized that continued detention, based solely on the sorts of misrepresentations alleged by the government, is exceedingly rare and clearly only in further retaliation for his speech on Palestine. \u201cThis is just another cruel attempt by the government to punish Mahmoud for his protected speech,\u201d said Marc Van Der Hout, founding partner at Van Der Hout LLP. \u201cDetaining someone on a charge like this is highly unusual and, frankly, outrageous. The district court soundly and clearly rejected DHS\u2019s attempt to deport Mahmoud for speaking out about the genocide in Gaza, and there continues to be no constitutional basis for his detention.\u201d The government\u2019s immigration case on the foreign policy grounds rested entirely on Secretary of State Marco Rubio\u2019s foreign policy \u201cdetermination,\u201d which the federal court has now enjoined. The government later added the unfounded allegations that Mr. Khalil had not disclosed his previous employment and associations accurately on his green card application. Mr. Khalil\u2019s legal team refuted those allegations with overwhelming evidence which the government did not even attempt to respond to. \u201cThis is a classic move from the government\u2019s playbook: make false claims and delay, delay, delay,\u201d said Amy Belsher, director of Immigrants\u2019 Rights Litigation at the NYCLU. \u201cThere\u2019s zero legitimate reason for Mahmoud Khalil to remain detained \u2014 it's clear that the government's outstanding charge is baseless and retaliatory. No more lies or dragging feet. Mahmoud must be released immediately to go home to his family and newborn son.\u201d \u201cThe government\u2019s decision to continue to detain Mahmoud on these patently false and pretextual charges is only more evidence of their cowardly vindictiveness toward him and their unrelenting desire to punish him for speaking out against them and their complicity in genocide,\u201d said Baher Azmy, legal director of the Center for Constitutional Rights. Mr. Khalil is represented by Dratel & Lewis, the Center for Constitutional Rights, CLEAR, Van Der Hout LLP, Washington Square Legal Services, the New York Civil Liberties Union (NYCLU), the ACLU of New Jersey, the ACLU of Louisiana, and the American Civil Liberties Union (ACLU).\", 'date': '12 days ago', 'datetime': '2025-06-06T04:12:38.989375', 'link': 'https://www.aclu.org/news/immigrants-rights/from-day-one-trumps-immigration-agenda-has-grown-more-extreme', 'source': 'American Civil Liberties Union', 'reporter': ['Sarah Mehta'], 'cos_sim': 0.20348650504527518}, {'title': 'Trump and Musk\u2019s relationship flames out just as intensely and publicly as it started', 'content': 'WASHINGTON (AP) \u2014 Donald Trump and Elon Musk\u2019s alliance took off like one of SpaceX\u2019s rockets. It was supercharged and soared high. And then it blew up.\\n\\nThe spectacular flameout Thursday peaked as Trump threatened to cut Musk\u2019s government contracts and Musk claimed that Trump\u2019s administration hasn\u2019t released all the records related to sex abuser Jeffrey Epstein because Trump is mentioned in them.\\n\\n...\\n\\n___\\n\\nAssociated Press writers Chris Megerian, Zeke Miller and Eric Tucker in Washington and Bernard Condon and Paul Harloff in New York contributed to this report.', 'date': '13 days ago', 'datetime': '2025-06-05T04:12:38.990273', 'link': 'https://apnews.com/article/trump-musk-tax-bill-6e7845081259c34db785182c51569c0c', 'source': 'AP News', 'reporter': ['Michelle L. Price'], 'cos_sim': 0.37471208297526104}, {'title': 'Trump ignored Newsom in putting the National Guard in LA. That\u2019s rare in US history', 'content': 'President Donald Trump\u2019s call-up of 2,000 citizen soldiers from the California National Guard against the wishes of Gov. Gavin Newsom has few precedents in U.S. history.\\n\\nTrump insists the federalized troops are necessary to protect immigration enforcement.\\n\\n...\\n\\nBut often protesters are arrested for failing to disperse, even if protesters struggle to leave the area quickly enough.\\n\\nIn that situation, \u201cyou\u2019re not going to be able to be arrested just because you\u2019re wearing a mask. I mean, they might arrest you, but it\u2019s a First Amendment violation.\u201d', 'date': '10 days ago', 'datetime': '2025-06-08T04:12:38.991072', 'link': 'https://calmatters.org/politics/2025/06/national-guard-los-angeles-legal/', 'source': 'CalMatters', 'reporter': ['Mikhail Zinshteyn'], 'cos_sim': 0.27830708783035496}, {'title': 'Trump says relationship with Musk is over', 'content': 'It came after the tech billionaire - who donated millions to Trump\\'s election campaign and became a White House aide - publicly criticised the president\\'s tax and spending bill, a key domestic policy.\\n\\nThe comments were Trump\\'s latest since the epic fallout between him and Musk unravelled on social media.\\n\\n...\\n\\nMusk, the world\\'s richest man, who donated roughly $250m to Trump\\'s presidential campaign, suggested during the social media feud that he might back some of Trump\\'s opponents during next year\\'s midterm elections, throwing his support behind challengers to the lawmakers who supported Trump\\'s tax bill.\\n\\nWhen asked about the prospect of Musk backing Democratic candidates that run against Republicans, Trump said he would face \"serious consequences\".', 'date': '11 days ago', 'datetime': '2025-06-07T04:12:38.992025', 'link': 'https://www.bbc.com/news/articles/c9wg240q0plo', 'source': 'BBC', 'reporter': ['Brandon Drenon'], 'cos_sim': 0.4059532093817478}, {'title': 'June 6, 2025: Donald Trump presidency news', 'content': 'Simon Sandoval-Moshenberg, Kilmar Abrego Garcia\u2019s attorney, said the government\u2019s move to bring his client back to the US to face federal criminal charges after a months-long legal battle \u201cshows that they were playing games with the court all along.\u201d\\n\\n\u201cDue process means the chance to defend yourself before you\u2019re punished, not after. This is an abuse of power, not justice,\u201d Sandoval-Moshenberg said in a statement.\\n\\n...\\n\\n\u201cNone of y\u2019all would have ever heard his name,\u201d the attorney said. \u201cBut instead, they chose to make this into a national cause c\u00e9l\u00e8bre, drag his name through the mud, and frankly, if they can do that to him, they can do that to any one of us.\u201d\\n\\nThis post has been updated with additional remarks from Sandoval-Moshenberg.', 'date': '12 days ago', 'datetime': '2025-06-06T04:12:38.992930', 'link': 'https://www.cnn.com/politics/live-news/trump-elon-musk-news-06-06-25', 'source': 'CNN', 'reporter': ['Adrienne Vogt', 'Elise Hammond', 'Tori B. Powell'], 'cos_sim': 0.3208678524347652}, {'title': \"No 'going back' for Elon Musk after calling for Trump impeachment, says Steve Bannon\", 'content': 'toggle caption Evan Vucci/AP\\n\\nElon Musk \"crossed the Rubicon\" when he echoed sentiments on his social media platform X, calling for President Trump to be impeached, says former Trump adviser Steve Bannon.\\n\\n...\\n\\nNote: Trump is currently serving his second and final constitutionally allowed term as president. Trump told CNN Friday that he won\\'t speak to Musk \"for a while.\"\\n\\nThis digital story was edited by Treye Green. The radio version was edited by Reena Advani and produced by Barry Gordemer, Julie Depenbrock and Nia Dumas.', 'date': '12 days ago', 'datetime': '2025-06-06T04:12:38.993809', 'link': 'https://www.npr.org/2025/06/06/nx-s1-5424732/trump-musk-feud-steve-bannon', 'source': 'NPR', 'reporter': ['Steve Inskeep'], 'cos_sim': 0.34704321478436717}, {'title': \"Trump tells ABC Musk 'lost his mind,' as CEO's dad says 'make sure this fizzles out'\", 'content': 'President Donald Trump attends a meeting with the Fraternal Order of Police in the State Dinning Room of the White House, June 5, 2025, in Washington.\\n\\nPresident Donald Trump attends a meeting with the Fraternal Order of Police in the State Dinning Room of the White House, June 5, 2025, in Washington.\\n\\n...\\n\\n\"Good advice,\" Musk responded to the user. \"Ok, we won\\'t decommission Dragon.\"\\n\\nABC News\\' Will Steakin and Lalee Ibssa contributed to this report.', 'date': '12 days ago', 'datetime': '2025-06-06T04:12:38.994659', 'link': 'https://abcnews.go.com/Politics/day-after-blistering-exchange-trump-calls-elon-musk/story?id=122567621', 'source': 'ABC News', 'reporter': ['Jonathan Karl'], 'cos_sim': 0.3700057435287639}]"
#   },
#   {
#     "role": "assistant",
#     "name": "work_agent",
#     "tool_calls": [
#       {
#         "type": "function",
#         "id": "call_JYnRDSpZvFAU9eSYy7MXHlyO",
#         "function": {
#           "name": "transfer_to_review_agent",
#           "arguments": "{}"
#         }
#       }
#     ],
#     "content": "### Top 5 News Articles on Trump\n\n#### 1. **Trump says Musk will face 'serious consequences' if he funds Democratic candidates**\n   - **Summary**: Former President Donald Trump warned Elon Musk of \"serious consequences\" if he financially supports Democratic candidates. This statement came amidst tensions between the two, with Musk expressing frustrations over Trump's policies and hinting at backing opposition candidates.\n   - **Source**: [NBC News](https://www.nbcnews.com/politics/donald-trump/trump-elon-musk-consequences-funds-democratic-candidates-rcna211605)\n   - **Date**: 11 days ago\n\n#### 2. **Trump and Musk\u2019s relationship flames out just as intensely and publicly as it started**\n   - **Summary**: The once-strong alliance between Trump and Musk has deteriorated, with Trump threatening to cut Musk's government contracts and Musk accusing Trump of withholding records related to Jeffrey Epstein. The fallout has been highly publicized.\n   - **Source**: [AP News](https://apnews.com/article/trump-musk-tax-bill-6e7845081259c34db785182c51569c0c)\n   - **Date**: 13 days ago\n\n#### 3. **Trump says relationship with Musk is over**\n   - **Summary**: Trump declared his relationship with Musk officially over after Musk criticized Trump's tax and spending bill. Musk hinted at supporting Democratic candidates, further escalating tensions between the two.\n   - **Source**: [BBC](https://www.bbc.com/news/articles/c9wg240q0plo)\n   - **Date**: 11 days ago\n\n#### 4. **No 'going back' for Elon Musk after calling for Trump impeachment, says Steve Bannon**\n   - **Summary**: Steve Bannon commented that Musk \"crossed the Rubicon\" by calling for Trump's impeachment. This marks a significant shift in Musk's stance, as he previously supported Trump during his campaigns.\n   - **Source**: [NPR](https://www.npr.org/2025/06/06/nx-s1-5424732/trump-musk-feud-steve-bannon)\n   - **Date**: 12 days ago\n\n#### 5. **Trump tells ABC Musk 'lost his mind,' as CEO's dad says 'make sure this fizzles out'**\n   - **Summary**: Trump criticized Musk, claiming he \"lost his mind\" following their public feud. Musk's father also weighed in, advising Musk to de-escalate the situation. The feud has drawn significant media attention.\n   - **Source**: [ABC News](https://abcnews.go.com/Politics/day-after-blistering-exchange-trump-calls-elon-musk/story?id=122567621)\n   - **Date**: 12 days ago\n\n---\n\nI will now review the summaries for accuracy and coherence."
#   },
#   {
#     "role": "tool",
#     "name": "transfer_to_review_agent",
#     "tool_call_id": "call_JYnRDSpZvFAU9eSYy7MXHlyO",
#     "content": "Successfully transferred to review_agent"
#   },
#   {
#     "role": "assistant",
#     "name": "review_agent",
#     "content": "The review highlights several areas for improvement in the summaries provided. While the content is clear and informative, it could benefit from enhanced context, consistent tone, and a more engaging structure. Incorporating these suggestions would make the summaries more professional and reader-friendly. Let me know if you'd like me to revise the summaries accordingly!"
#   },
#   {
#     "role": "assistant",
#     "name": "review_agent",
#     "tool_calls": [
#       {
#         "type": "function",
#         "id": "6606d61c-9573-42d9-803c-1ba3138ffc56",
#         "function": {
#           "name": "transfer_back_to_supervisor",
#           "arguments": "{}"
#         }
#       }
#     ],
#     "content": "Transferring back to supervisor"
#   },
#   {
#     "role": "tool",
#     "name": "transfer_back_to_supervisor",
#     "tool_call_id": "6606d61c-9573-42d9-803c-1ba3138ffc56",
#     "content": "Successfully transferred back to supervisor"
#   },
#   {
#     "role": "assistant",
#     "name": "supervisor",
#     "tool_calls": [
#       {
#         "type": "function",
#         "id": "call_LkGof5vs0hcQXDlNcgi89QP1",
#         "function": {
#           "name": "transfer_to_review_agent",
#           "arguments": "{}"
#         }
#       }
#     ],
#     "content": ""
#   },
#   {
#     "role": "tool",
#     "name": "transfer_to_review_agent",
#     "tool_call_id": "call_LkGof5vs0hcQXDlNcgi89QP1",
#     "content": "Successfully transferred to review_agent"
#   },
#   {
#     "role": "assistant",
#     "name": "review_agent",
#     "content": "The review process has identified areas for improvement in the summaries provided for the top 5 news articles on Trump. Here's a detailed breakdown of the feedback:\n\n### Strengths:\n1. **Clarity**: The summaries are clear and concise, making it easy for readers to understand the key points of each article.\n2. **Organization**: The content is well-structured, with each article summary followed by its source and publication date.\n3. **Accuracy**: The summaries accurately reflect the content of the articles, ensuring that readers get a reliable overview.\n\n### Areas for Improvement:\n1. **Title Specificity**: The title \"Top 5 News Articles on Trump\" is generic. A more specific title, such as \"Top 5 News Articles on Trump and Musk's Public Feud,\" would immediately inform readers about the focus of the content.\n2. **Contextual Background**: The summaries assume readers are familiar with the Trump-Musk relationship. Adding a brief introductory paragraph to provide context about their history and why this feud is significant would enhance the content.\n3. **Consistency in Detail**: The level of detail varies between summaries. For example, Article 2 includes more context about the fallout, while Article 3 is more straightforward. Aim for a consistent depth of analysis across all summaries.\n4. **Engagement**: The summaries are informative but lack a sense of engagement. Adding a question or call-to-action at the end, such as \"What do you think about the escalating tensions between Trump and Musk?\" could encourage reader interaction.\n5. **Source Credibility**: The inclusion of publication dates (e.g., \"11 days ago\") feels vague. Replace this with specific dates (e.g., \"October 15, 2023\") for clarity and professionalism.\n6. **Grammar and Style**: Some sentences could be rephrased for smoother readability. For instance, in Article 5, \"Musk's father also weighed in, advising Musk to de-escalate the situation\" could be rephrased as \"Musk's father weighed in, urging him to de-escalate the feud.\"\n\n### Revised Example:\n#### 1. **Trump Warns Musk of 'Serious Consequences' Over Democratic Support**\n   - **Summary**: Former President Donald Trump issued a stark warning to Elon Musk, threatening \"serious consequences\" if the billionaire supports Democratic candidates. This statement follows Musk's public frustrations with Trump's policies and hints at backing opposition candidates, further straining their relationship.\n   - **Source**: [NBC News](https://www.nbcnews.com/politics/donald-trump/trump-elon-musk-consequences-funds-democratic-candidates-rcna211605)\n   - **Date**: October 15, 2023\n\nBy implementing these changes, the content will be more engaging, professional, and accessible to a broader audience. Let me know if you'd like me to revise the summaries accordingly!"
#   },
#   {
#     "role": "assistant",
#     "name": "review_agent",
#     "tool_calls": [
#       {
#         "type": "function",
#         "id": "56c57168-88fd-4759-8498-560646fbf41c",
#         "function": {
#           "name": "transfer_back_to_supervisor",
#           "arguments": "{}"
#         }
#       }
#     ],
#     "content": "Transferring back to supervisor"
#   },
#   {
#     "role": "tool",
#     "name": "transfer_back_to_supervisor",
#     "tool_call_id": "56c57168-88fd-4759-8498-560646fbf41c",
#     "content": "Successfully transferred back to supervisor"
#   },
#   {
#     "role": "assistant",
#     "name": "supervisor",
#     "content": "The summaries provided are generally accurate and coherent, but they could benefit from slight refinements for clarity and engagement. Here's a detailed critique:\n\n### Review of Summaries\n\n#### 1. **Trump says Musk will face 'serious consequences' if he funds Democratic candidates**\n   - **Accuracy**: The summary captures the essence of the article, focusing on Trump's warning to Musk. However, it could include more details about the context of Musk's frustrations with Trump's policies.\n   - **Coherence**: The summary is coherent but could be more engaging by emphasizing the implications of Musk's potential support for Democrats.\n\n#### 2. **Trump and Musk\u2019s relationship flames out just as intensely and publicly as it started**\n   - **Accuracy**: The summary is accurate, highlighting the fallout between Trump and Musk. Adding specifics about the government contracts and Epstein records would provide more depth.\n   - **Coherence**: The summary flows well but could be improved by linking the events to their broader political implications.\n\n#### 3. **Trump says relationship with Musk is over**\n   - **Accuracy**: The summary accurately reflects the article's content. Including Musk's criticisms of the tax and spending bill would add context.\n   - **Coherence**: The summary is clear but could be more engaging by exploring the impact of Musk's hinted support for Democrats.\n\n#### 4. **No 'going back' for Elon Musk after calling for Trump impeachment, says Steve Bannon**\n   - **Accuracy**: The summary is accurate but lacks details about Musk's previous support for Trump and the reasons behind his call for impeachment.\n   - **Coherence**: The summary is coherent but could be more compelling by emphasizing the significance of Musk's shift in stance.\n\n#### 5. **Trump tells ABC Musk 'lost his mind,' as CEO's dad says 'make sure this fizzles out'**\n   - **Accuracy**: The summary captures the main points but could include more details about Musk's father's advice and its implications.\n   - **Coherence**: The summary is coherent but could be more engaging by exploring the broader context of the feud.\n\n---\n\n### Suggestions for Improvement\n1. **Add Context**: Include more details about the events leading to the feud and their implications.\n2. **Enhance Engagement**: Use a more dynamic tone to make the summaries more compelling.\n3. **Consistency**: Ensure a consistent structure across all summaries for a professional presentation.\n\nLet me know if you'd like me to revise the summaries based on these suggestions!"
#   },
#   {
#     "role": "assistant",
#     "name": "supervisor",
#     "content": "Would you like me to revise the summaries based on the detailed critique provided?"
#   }
# ]
    
#     # Create evaluator
#     evaluator = create_trajectory_match_evaluator(
#         trajectory_match_mode="unordered"
#     )
    
#     # Evaluate
#     result = evaluator(
#         outputs=outputs,
#         reference_outputs=reference_outputs
#     )
#     print(result)
#     print('\n')
#     evaluator = create_trajectory_match_evaluator(
#         trajectory_match_mode="subset"
#     )
    
#     # Evaluate
#     result = evaluator(
#         outputs=outputs,
#         reference_outputs=reference_outputs
#     )
#     print(result)
#     print('\n')
#     evaluator = create_trajectory_match_evaluator(
#         trajectory_match_mode="superset"
#     )
    
#     # Evaluate
#     result = evaluator(
#         outputs=outputs,
#         reference_outputs=reference_outputs
#     )
#     print(result)
#     print('\n')
#     evaluator_unordered = create_trajectory_match_evaluator(
#         trajectory_match_mode="unordered",
#         tool_args_match_overrides={
#             "get_related_news_tool": lambda x, y: x["topic"].lower() == y["topic"].lower()
#         }
#     )
    
#     result_unordered = evaluator_unordered(
#         outputs=outputs,
#         reference_outputs=reference_outputs
#     )
    
#     print("Unordered evaluation result:")
#     print(result_unordered)
#     print('\n')

#     return outputs
    
    



import json
import time
from agentevals.trajectory.match import create_trajectory_match_evaluator
from src.essay_agent.graph.run_graph import run_multi_agent_workflow_silent
from langchain_core.messages import convert_to_openai_messages

def get_reference_outputs():
    """Store all reference outputs for different prompts"""
    return {
        "Tell me about black holes in short.": [{'role': 'user', 'content': 'Tell me about black holes in short.'}, {'role': 'assistant', 'name': 'supervisor', 'tool_calls': [], 'content': ''}, {'role': 'assistant', 'name': 'work_agent', 'content': 'A black hole is a region in space where gravity is so strong that nothing—not even light—can escape from it. It forms when a massive star collapses under its own gravity at the end of its life.\n\nBlack holes have an invisible boundary called the event horizon, beyond which no information can return. At their core lies a singularity, a point of infinite density where the known laws of physics break down.\n\nThey come in different sizes—stellar (a few times the Sun’s mass), supermassive (millions to billions of solar masses at galaxy centers), and possibly intermediate ones. Despite being invisible, black holes are detected through their effects on nearby stars, gas, and light—such as powerful X-ray emissions or gravitational waves.'}],
        "find 5 related news articles on trump , then review the summary for accuracy and coherence.": [{'role': 'user', 'content': 'find 5 related news articles on trump , then review the summary for accuracy and coherence.'}, {'role': 'assistant', 'name': 'supervisor', 'tool_calls': [{'type': 'function', 'id': 'call_5Tt4zb0acW674cX7xm5HBJzw', 'function': {'name': 'transfer_to_work_agent', 'arguments': '{}'}}], 'content': ''}, {'role': 'tool', 'name': 'transfer_to_work_agent', 'tool_call_id': 'call_5Tt4zb0acW674cX7xm5HBJzw', 'content': 'Successfully transferred to work_agent'}, {'role': 'assistant', 'name': 'work_agent', 'content': 'Here are the top 5 related news articles on Trump:\n\n### 1. Morning Report — Trump sprints to the high court with emergency appeals\n**Summary:** This article discusses former President Donald Trump\'s recent emergency appeals to the Supreme Court. The appeals are part of his ongoing legal battles and efforts to overturn various decisions.\n**Source:** [The Hill](https://thehill.com/newsletters/morning-report/5329781-donald-trump-high-court-appeals/)\n**Date:** 24 days ago\n\n### 2. Trump says Musk will face \'serious consequences\' if he funds Democratic candidates\n**Summary:** In a phone interview with NBC News, Trump warned Elon Musk of "serious consequences" if he funds Democratic candidates. The article highlights the tension between Trump and Musk, with Trump criticizing Musk\'s involvement in politics.\n**Source:** [NBC News](https://www.nbcnews.com/politics/donald-trump/trump-elon-musk-consequences-funds-democratic-candidates-rcna211605)\n**Date:** 20 days ago\n\n### 3. Read Trump’s memo asking Congress to take back approved funding for foreign aid, PBS, NPR\n**Summary:** This article provides details on Trump\'s memo to Congress requesting the rescission of approved funding for foreign aid, PBS, and NPR. The memo is part of Trump\'s broader efforts to cut government spending on what he deems unnecessary programs.\n**Source:** [PBS](https://www.pbs.org/newshour/politics/read-trumps-full-memo-asking-congress-to-claw-back-approved-spending-targeted-by-doge)\n**Date:** 24 days ago\n\n### 4. Trump administration presents details of budget cuts\n**Summary:** The Trump administration has proposed significant budget cuts to federal housing and health care programs, while increasing funding for the military. The proposed budget also includes cuts to Amtrak and other federal programs.\n**Source:** [NJ Spotlight News](https://www.njspotlightnews.org/2025/06/new-documents-show-extent-of-trump-administrations-budget-cutting-aims/)\n**Date:** 23 days ago\n\n### 5. Trump and Musk\'s relationship flames out just as intensely as it started\n**Summary:** The article describes the fallout between Trump and Elon Musk, highlighting their initial strong alliance and subsequent public disputes. The conflict has escalated to threats and accusations from both sides.\n**Source:** [AP News](https://apnews.com/article/trump-musk-tax-bill-6e7845081259c34db785182c51569c0c)\n**Date:** 22 days ago\n\nThese articles provide a comprehensive overview of recent news related to Donald Trump, covering his legal battles, political conflicts, budget proposals, and more.'}, {'role': 'assistant', 'name': 'work_agent', 'tool_calls': [{'type': 'function', 'id': '7f5b1085-a706-4167-97ee-98264f4b8123', 'function': {'name': 'transfer_back_to_supervisor', 'arguments': '{}'}}], 'content': 'Transferring back to supervisor'}, {'role': 'tool', 'name': 'transfer_back_to_supervisor', 'tool_call_id': '7f5b1085-a706-4167-97ee-98264f4b8123', 'content': 'Successfully transferred back to supervisor'}, {'role': 'assistant', 'name': 'supervisor', 'tool_calls': [{'type': 'function', 'id': 'call_fOBty65UyXaGTgfAtAtBZnYX', 'function': {'name': 'transfer_to_review_agent', 'arguments': '{}'}}], 'content': ''}, {'role': 'tool', 'name': 'transfer_to_review_agent', 'tool_call_id': 'call_fOBty65UyXaGTgfAtAtBZnYX', 'content': 'Successfully transferred to review_agent'}, {'role': 'assistant', 'name': 'review_agent', 'content': "Here is the detailed feedback on the summaries of the five articles related to Trump:\n\n### 1. Morning Report — Trump sprints to the high court with emergency appeals\n**Feedback:**\n- **Relevance:** The summary is relevant to the article's content.\n- **Completeness:** The summary is concise but lacks specific details about the nature of the decisions Trump is trying to overturn and the legal arguments presented.\n- **Accuracy:** The summary accurately reflects the general topic of the article.\n- **Quality:** The summary is clear but could be more engaging with additional context.\n- **Specific Issues:** Adding more context about the specific cases and potential implications would improve the summary.\n\n### 2. Trump says Musk will face 'serious consequences' if he funds Democratic candidates\n**Feedback:**\n- **Relevance:** The summary is relevant to the article's content.\n- **Completeness:** The summary provides a basic overview but lacks context and detail about the background and significance of the situation.\n- **Accuracy:** The summary accurately reflects the main point of the article.\n- **Quality:** The summary is clear but could be more informative with additional context and quotes.\n- **Specific Issues:** Including more context about the tension between Trump and Musk, as well as direct quotes, would enhance the summary.\n\n### 3. Read Trump’s memo asking Congress to take back approved funding for foreign aid, PBS, NPR\n**Feedback:**\n- **Relevance:** The summary is relevant to the article's content.\n- **Completeness:** The summary provides a basic overview but lacks details about the rationale behind the memo and the potential impact of the proposed cuts.\n- **Accuracy:** The summary accurately reflects the main point of the article.\n- **Quality:** The summary is clear but could be more informative with additional context and perspectives.\n- **Specific Issues:** Adding context about the rationale for the cuts, potential impacts, and perspectives from both supporters and critics would improve the summary.\n\n### 4. Trump administration presents details of budget cuts\n**Feedback:**\n- **Relevance:** The summary is relevant to the article's content.\n- **Completeness:** The summary provides a basic overview but lacks details about the rationale behind the budget changes and their potential impact.\n- **Accuracy:** The summary accurately reflects the main point of the article.\n- **Quality:** The summary is clear but could be more informative with additional context and specifics.\n- **Specific Issues:** Including context about the rationale for the budget changes, potential impacts, and specific figures would enhance the summary.\n\n### 5. Trump and Musk's relationship flames out just as intensely as it started\n**Feedback:**\n- **Relevance:** The summary is relevant to the article's content.\n- **Completeness:** The summary provides a basic overview but lacks specific details about the nature of the initial alliance and the specific incidents that led to the fallout.\n- **Accuracy:** The summary accurately reflects the main point of the article.\n- **Quality:** The summary is clear but could be more engaging with additional context and quotes.\n- **Specific Issues:** Adding background information, details about the disputes, direct quotes, and contextualizing the conflict would improve the summary.\n\nOverall, the summaries provide a good foundation but could be enhanced with additional details, context, and perspectives to make them more informative and engaging for readers."}, {'role': 'assistant', 'name': 'review_agent', 'tool_calls': [{'type': 'function', 'id': '413ccd11-86ba-40c2-a74a-8338ae438a8d', 'function': {'name': 'transfer_back_to_supervisor', 'arguments': '{}'}}], 'content': 'Transferring back to supervisor'}, {'role': 'tool', 'name': 'transfer_back_to_supervisor', 'tool_call_id': '413ccd11-86ba-40c2-a74a-8338ae438a8d', 'content': 'Successfully transferred back to supervisor'}, {'role': 'assistant', 'name': 'supervisor', 'content': 'The review of the summaries is complete. The feedback highlights areas for improvement in terms of adding more context, details, and perspectives to make the summaries more informative and engaging. If you need any further assistance or revisions, please let me know!'}],
        "find 5 related news articles on walmart": [{'role': 'user', 'content': 'find 5 related news articles on walmart'}, {'role': 'assistant', 'name': 'supervisor', 'tool_calls': [{'type': 'function', 'id': 'call_UXF8Bpqr5MGoQiqGHJJVXOOf', 'function': {'name': 'transfer_to_work_agent', 'arguments': '{}'}}], 'content': ''}, {'role': 'tool', 'name': 'transfer_to_work_agent', 'tool_call_id': 'call_UXF8Bpqr5MGoQiqGHJJVXOOf', 'content': 'Successfully transferred to work_agent'}, {'role': 'assistant', 'name': 'work_agent', 'content': '### Top 5 Related News Articles on Walmart\n\n#### 1. Walmart Takes Flight With Drone Delivery Expansion to Five New Cities, Redefining Fast, Flexible Retail\n- **Summary**: Walmart is expanding its drone delivery service to five new cities, including Atlanta, Charlotte, Houston, Orlando, and Tampa. This expansion, in partnership with Wing, aims to provide faster and more efficient delivery services.\n- **Source**: [Walmart](https://corporate.walmart.com/news/2025/06/05/walmart-takes-flight-with-drone-delivery-expansion-to-5-new-cities-redefining-fast-flexible-retail)\n- **Date**: 21 days ago\n\n#### 2. Walmart to Expand Drone Delivery to 5 More Cities\n- **Summary**: Walmart, in collaboration with Wing, is set to expand its drone delivery program to five additional cities, reaching millions of new customers. The service will include thousands of items, such as fresh produce and household essentials.\n- **Source**: [Supply Chain Dive](https://www.supplychaindive.com/news/walmart-wing-drone-delivery-availability-expansion/750072/)\n- **Date**: 20 days ago\n\n#### 3. Walmart Challenges Consumer Perceptions with ‘Who Knew?’ Campaign\n- **Summary**: Walmart has launched a new campaign, "Who Knew?", featuring actors Walton Goggins and Stephanie Beatriz. The campaign aims to challenge consumer perceptions and highlight the various perks of shopping at Walmart.\n- **Source**: [Marketing Dive](https://www.marketingdive.com/news/walmart-challenges-consumer-perceptions-with-who-knew-campaign/750112/)\n- **Date**: 17 days ago\n\n#### 4. Walmart CEO McMillon Talks Wages, Worker Education, and Tariffs\n- **Summary**: Walmart CEO Doug McMillon discussed the company\'s efforts to raise wages, invest in worker education, and navigate tariffs. He highlighted significant wage increases and investments in skills training and education programs.\n- **Source**: [Talk Business & Politics](https://talkbusiness.net/2025/06/walmart-ceo-mcmillon-talks-wages-worker-education-and-tariffs/)\n- **Date**: 20 days ago\n\n#### 5. Walmart Debuts Sparky, Its Generative AI Assistant for Customers\n- **Summary**: Walmart has introduced Sparky, a generative AI assistant designed to help customers by summarizing reviews, offering recommendations, and assisting with purchase planning. This initiative is part of Walmart\'s broader AI integration plans.\n- **Source**: [Retail Dive](https://www.retaildive.com/news/walmart-launches-generative-ai-assistant-sparky/750300/)\n- **Date**: 16 days ago\n\nThese articles provide a comprehensive overview of Walmart\'s recent initiatives and developments, including technological advancements, marketing campaigns, and corporate strategies.'}, {'role': 'assistant', 'name': 'work_agent', 'tool_calls': [{'type': 'function', 'id': '3ccd1290-249d-4ea5-9f6d-a6da4d47e366', 'function': {'name': 'transfer_back_to_supervisor', 'arguments': '{}'}}], 'content': 'Transferring back to supervisor'}, {'role': 'tool', 'name': 'transfer_back_to_supervisor', 'tool_call_id': '3ccd1290-249d-4ea5-9f6d-a6da4d47e366', 'content': 'Successfully transferred back to supervisor'}, {'role': 'assistant', 'name': 'supervisor', 'content': 'The work_agent has found 5 related news articles on Walmart. Would you like the review_agent to critique the generated content?'}],
        "take this document pdfs/IPCC_AR6_SYR_SPM.pdf and give summary, review the generated content" : [{'role': 'user', 'content': 'take this document pdfs/IPCC_AR6_SYR_SPM.pdf and give summary, review the generated content'}, {'role': 'assistant', 'name': 'supervisor', 'tool_calls': [{'type': 'function', 'id': 'call_5PJaCJiSGyuQJ7p8uoPEwfID', 'function': {'name': 'transfer_to_work_agent', 'arguments': '{}'}}], 'content': ''}, {'role': 'tool', 'name': 'transfer_to_work_agent', 'tool_call_id': 'call_5PJaCJiSGyuQJ7p8uoPEwfID', 'content': 'Successfully transferred to work_agent'}, {'role': 'assistant', 'name': 'work_agent', 'content': 'The document has been successfully transferred for review. You will receive a summary and reviewed content shortly.'}, {'role': 'assistant', 'name': 'work_agent', 'tool_calls': [{'type': 'function', 'id': '29a9b28e-5a70-427f-9cee-3be4742ce519', 'function': {'name': 'transfer_back_to_supervisor', 'arguments': '{}'}}], 'content': 'Transferring back to supervisor'}, {'role': 'tool', 'name': 'transfer_back_to_supervisor', 'tool_call_id': '29a9b28e-5a70-427f-9cee-3be4742ce519', 'content': 'Successfully transferred back to supervisor'}, {'role': 'assistant', 'name': 'supervisor', 'tool_calls': [{'type': 'function', 'id': 'call_mMkw3iDzYduJIC5buMhrE0rX', 'function': {'name': 'transfer_to_review_agent', 'arguments': '{}'}}], 'content': ''}, {'role': 'tool', 'name': 'transfer_to_review_agent', 'tool_call_id': 'call_mMkw3iDzYduJIC5buMhrE0rX', 'content': 'Successfully transferred to review_agent'}, {'role': 'assistant', 'name': 'review_agent', 'content': "The review tool has provided feedback on the generated content."}, {'role': 'assistant', 'name': 'review_agent', 'tool_calls': [{'type': 'function', 'id': '65d565da-717a-4347-939e-04f2eae69149', 'function': {'name': 'transfer_back_to_supervisor', 'arguments': '{}'}}], 'content': 'Transferring back to supervisor'}, {'role': 'tool', 'name': 'transfer_back_to_supervisor', 'tool_call_id': '65d565da-717a-4347-939e-04f2eae69149', 'content': 'Successfully transferred back to supervisor'}, {'role': 'assistant', 'name': 'supervisor', 'content': "Short Summary (IPCC AR6 Synthesis Report): The 2023 IPCC Synthesis Report concludes that human activities have unequivocally caused global warming of about 1.1\u00b0C since pre-industrial times. Limiting warming requires immediate large-scale emissions reductions, equitable adaptation, and enhanced global cooperation."}]
    }


# def extract_messages_from_chunks(chunks):
#     """Extract and convert messages from workflow chunks to OpenAI format"""
#     all_messages = []
#     for chunk in chunks:
#         for key, value in chunk.items():
#             if key in ['supervisor', 'work_agent', 'review_agent'] and isinstance(value, dict):
#                 # Extract messages from agent responses
#                 if 'messages' in value and isinstance(value['messages'], list):
#                     all_messages.extend(value['messages'])
#             elif key == 'messages' and isinstance(value, list):
#                 # Direct messages in chunk
#                 all_messages.extend(value)
    
#     # Convert to OpenAI format
#     outputs = []
#     if all_messages:
#         try:
#             outputs = convert_to_openai_messages(all_messages)
#         except Exception as e:
#             print(f"Error converting to OpenAI format: {e}")
#             # Fallback: manual conversion
#             for msg in all_messages:
#                 try:
#                     if hasattr(msg, 'type'):
#                         role_mapping = {
#                             'human': 'user',
#                             'ai': 'assistant',
#                             'system': 'system',
#                             'tool': 'tool'
#                         }
#                         role = role_mapping.get(msg.type, 'user')
#                         content = getattr(msg, 'content', str(msg))
                        
#                         openai_msg = {'role': role, 'content': content}
                        
#                         # Handle tool calls if present
#                         if hasattr(msg, 'tool_calls') and msg.tool_calls:
#                             openai_msg['tool_calls'] = msg.tool_calls
                        
#                         # Handle tool call id if present
#                         if hasattr(msg, 'tool_call_id') and msg.tool_call_id:
#                             openai_msg['tool_call_id'] = msg.tool_call_id
                            
#                         outputs.append(openai_msg)
                        
#                 except Exception as msg_error:
#                     print(f"Error processing message: {msg_error}")
#                     continue
    
#     return outputs
def extract_messages_from_chunks(chunks):
    """Extract messages from streaming chunks, handling both dict and tuple formats"""
    all_messages = []
    
    for chunk in chunks:
        # Handle tuple format from subgraphs=True
        if isinstance(chunk, tuple):
            # chunk is (path_tuple, data_dict)
            path_tuple, data_dict = chunk
            
            # Extract messages from different sections
            for section_name, section_data in data_dict.items():
                if isinstance(section_data, dict) and 'messages' in section_data:
                    messages = section_data['messages']
                    if isinstance(messages, list):
                        all_messages.extend(messages)
                    else:
                        all_messages.append(messages)
        
        # Handle regular dict format
        elif isinstance(chunk, dict):
            for key, value in chunk.items():
                if isinstance(value, dict) and 'messages' in value:
                    messages = value['messages']
                    if isinstance(messages, list):
                        all_messages.extend(messages)
                    else:
                        all_messages.append(messages)
    
    # Convert to OpenAI format
    outputs = []
    if all_messages:
        try:
            outputs = convert_to_openai_messages(all_messages)
        except Exception as e:
            print(f"Error converting to OpenAI format: {e}")
            # Fallback: manual conversion
            for msg in all_messages:
                try:
                    if hasattr(msg, 'type'):
                        role_mapping = {
                            'human': 'user',
                            'ai': 'assistant',
                            'system': 'system',
                            'tool': 'tool'
                        }
                        role = role_mapping.get(msg.type, 'user')
                        content = getattr(msg, 'content', str(msg))
                        
                        openai_msg = {'role': role, 'content': content}
                        
                        # Add agent name if present
                        if hasattr(msg, 'name') and msg.name:
                            openai_msg['name'] = msg.name
                        
                        # Handle tool calls if present
                        if hasattr(msg, 'tool_calls') and msg.tool_calls:
                            openai_msg['tool_calls'] = []
                            for tool_call in msg.tool_calls:
                                if hasattr(tool_call, 'name'):
                                    # LangChain ToolCall format
                                    openai_msg['tool_calls'].append({
                                        'type': 'function',
                                        'id': getattr(tool_call, 'id', 'unknown'),
                                        'function': {
                                            'name': tool_call.name,
                                            'arguments': json.dumps(getattr(tool_call, 'args', {}))
                                        }
                                    })
                                else:
                                    # Already in OpenAI format
                                    openai_msg['tool_calls'].append(tool_call)
                        
                        # Handle tool call id if present
                        if hasattr(msg, 'tool_call_id') and msg.tool_call_id:
                            openai_msg['tool_call_id'] = msg.tool_call_id
                            
                        outputs.append(openai_msg)
                        
                except Exception as msg_error:
                    print(f"Error processing message: {msg_error}")
                    continue
    
    return outputs

def run_trajectory_evaluations(outputs, reference_outputs, user_message):
    """Run all trajectory evaluations and return results"""
    print(f"\n=== TRAJECTORY EVALUATION FOR: {user_message} ===")
    
    # Create evaluators
    evaluators = {
        "unordered": create_trajectory_match_evaluator(trajectory_match_mode="unordered"),
        "subset": create_trajectory_match_evaluator(trajectory_match_mode="subset"),
        "superset": create_trajectory_match_evaluator(trajectory_match_mode="superset"),
        "unordered_with_overrides": create_trajectory_match_evaluator(
            trajectory_match_mode="unordered",
            tool_args_match_overrides={
                "get_related_news_tool": lambda x, y: x["topic"].lower() == y["topic"].lower()
            }
        )
    }
    
    results = {}
    for eval_name, evaluator in evaluators.items():
        try:
            result = evaluator(
                outputs=outputs,
                reference_outputs=reference_outputs
            )
            results[eval_name] = result
            print(f"\n{eval_name.upper()} evaluation result:")
            print(result)
        except Exception as e:
            print(f"Error in {eval_name} evaluation: {e}")
            results[eval_name] = None
    
    return results

def evaluate_tool_usage(user_message: str, reference_outputs: list = None):
    """Evaluate tool usage against expected tools for a single prompt"""
    
    # Run the workflow and get results
    chunks = run_multi_agent_workflow_silent(user_message)
    
    # Extract and convert messages
    outputs = extract_messages_from_chunks(chunks)
    
    # Use provided reference outputs or get from storage
    if reference_outputs is None:
        reference_data = get_reference_outputs()
        reference_outputs = reference_data.get(user_message, [])
        if not reference_outputs:
            print(f"WARNING: No reference output found for prompt: {user_message}")
            return outputs, {}
    
    # Run trajectory evaluations
    trajectory_results = run_trajectory_evaluations(outputs, reference_outputs, user_message)
    
    return outputs, trajectory_results

def evaluate_multiple_prompts(prompts: list):
    """Evaluate multiple prompts and return aggregated results"""
    reference_data = get_reference_outputs()
    all_results = {}
    
    for i, user_message in enumerate(prompts, 1):
        if i > 1:
            time.sleep(5)  # Pause to respect API rate limits
        print(f"\n{'='*80}")
        print(f"EVALUATING PROMPT {i}: {user_message}")
        print(f"{'='*80}")
        
        # Check if we have reference output for this prompt
        if user_message not in reference_data:
            print(f"WARNING: No reference output found for prompt: {user_message}")
            all_results[user_message] = {'error': 'No reference output found'}
            continue
        
        try:
            reference_outputs = reference_data[user_message]
            outputs, trajectory_results = evaluate_tool_usage(user_message, reference_outputs)
            
            all_results[user_message] = {
                'outputs': outputs,
                'trajectory_results': trajectory_results
            }
            
        except Exception as e:
            print(f"Error evaluating prompt {i}: {e}")
            all_results[user_message] = {'error': str(e)}
    
    return all_results