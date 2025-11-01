from experta import *


class UserResponse(Fact):
    rule_number = Field(int, default=0)
    answered_yes = Field(bool, default=False)
    points_added = Field(int, default=0)


class Diagnosis(Fact):
    total_score = Field(int, default=0)
    severity = Field(str, default="Unclassified")


class ADHDDiagnosis(KnowledgeEngine):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.points = 0


        self.rules_data = {
            1: 1, 2: 2, 3: 3, 4: 1, 5: 2, 6: 3,
            7: 1, 8: 2, 9: 3, 10: 1, 11: 2, 12: 3
        }


        self.rules_text = {
            1:  "Do you feel restless or find it difficult to stay calm?",
            2:  "Do you fidget with your hands or feet or tap things while sitting?",
            3:  "Do you often leave your seat when you're expected to remain seated?",
            4:  "Do you find it difficult to work or play in a quiet environment?",
            5:  "Do you talk a lot or frequently interrupt others?",
            6:  "Do you run or move excessively in inappropriate places?",
            7:  "Do you start multiple tasks and rarely complete them?",
            8:  "Do you lose focus easily even during important or interesting activities?",
            9:  "Do you act on your emotions quickly (like anger or excitement without thinking)?",
            10: "Do you find it difficult to wait your turn in lines or conversations?",
            11: "Do you blurt out answers or say things without thinking about their appropriateness?",
            12: "Do you make important decisions or take big risks without thinking about long-term consequences?"
        }

    @DefFacts()
    def initial_fact(self):
        yield Fact(next_rule=1)

    @Rule(
        AS.f << Fact(next_rule=MATCH.rule_num),
        TEST(lambda rule_num: rule_num <= 12),
        salience=10
    )
    def ask_next_question(self, f, rule_num):
        self.retract(f)
        question = self.rules_text[rule_num]

        while True:
            answer = input(f"Q{rule_num} from 12: {question} (Answer with y/n): ").strip().lower()
            if answer in ['y', 'n']:
                is_yes = (answer == 'y')
                points = self.rules_data[rule_num] if is_yes else 0


                self.declare(UserResponse(
                    rule_number=rule_num,
                    answered_yes=is_yes,
                    points_added=points
                ))


                if rule_num < 12:
                    self.declare(Fact(next_rule=rule_num + 1))

                break
            else:
                print("incorrect answer. please answer 'y' for yes and 'n' for no.")

    @Rule(

        AS.response << UserResponse(answered_yes=True, points_added=P(lambda x: x > 0)),
        salience=20
    )
    def calculate_total_score(self, response):
        self.points += response['points_added']
        self.retract(response)

    @Rule(

        NOT(Fact(next_rule=P(lambda x: x <= 12))),
        salience=0
    )
    def determine_severity(self):
        score = self.points
        if score <= 6:
            severity = "Very mild symptoms or no initial diagnosis"
        elif 7 <= score <= 12:
            severity = "Mild Presentation"
        elif 13 <= score <= 18:
            severity = "Moderate Presentation - Formal assessment recommended"
        elif 19 <= score <= 24:
            severity = "Severe Presentation - Urgent need for formal assessment"
        else:
            severity = "Error in score calculation"

        print("\n==============================")
        print("✅ Initial Diagnosis Results for Hyperactive-Impulsive Pattern")
        print("==============================")
        print(f"Total Score: {score} out of 24 points.")
        print(f"Initial Severity Classification: {severity}")
        print("==============================")
        print("Remember: This is a preliminary assessment and does not replace consultation with a specialist.")


if __name__ == "__main__":
    engine = ADHDDiagnosis()
    print("ADHD-HI test starting...")
    engine.reset()
    engine.run()