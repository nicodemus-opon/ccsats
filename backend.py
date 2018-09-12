class Survey:
    #survey is a 3d array
    #level one contains questions
    #level two contains individual questions and types
    #level three contains the types
    questions = ["nico","bruce"]
    def parse_questions(self,qusetions):
        for x in questions:
            #x=individual questions and their types
            for que in x:
                actual_question=que[0]
                q_type=que[1][0]
                
    def delete_question():
        pass
    def get_questions():
        return(questions)
    def add_question(self,actual_question="",q_type=[]):
        list_of_question=[actual_question,q_type]
        questions.append(list_of_question)

myobjectx = Survey()

print(myobjectx.questions)
