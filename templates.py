# LinkedIn Post Templates

templates = {
    "personal_story": {
        "hook": "I failed at X — and it turned out to be the best thing that happened to my career.",
        "body": "Context: [Describe the situation]\nMistake: [What went wrong]\nLesson: [What I learned]\nTakeaway: [Actionable advice]",
        "cta": "What’s one mistake you learned from? I’ll read and reply."
    },
    "mini_list": {
        "hook": "5 quick things that improved our onboarding conversion by 30%.",
        "body": "- Tip 1\n- Tip 2\n- Tip 3\n- Tip 4\n- Tip 5",
        "cta": "Want the template? DM me."
    },
    "results_breakdown": {
        "hook": "How we cut support tickets by 42% in 6 weeks.",
        "body": "Problem: [Describe issue]\nApproach: [What we did]\nMetrics: [Results]\nChart: [Suggestion for image]",
        "cta": "If you want the playbook, comment ‘playbook’."
    },
    "opinion": {
        "hook": "Opinion: [Controversial statement].",
        "body": "Reason 1: [Explanation]\nReason 2: [Explanation]\nCounterpoint: [Address objection]",
        "cta": "Agree or disagree — what would you do differently?"
    }
}

def get_template(name):
    return templates.get(name, None)
