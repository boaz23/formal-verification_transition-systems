השלימו את הקוד עבור הפונקציות הבאות שלמדנו:

def pre(TS, C, a=None):
    raise NotImplementedError


def post(TS, C, a=None):
    raise NotImplementedError


def is_action_deterministic(TS):
    raise NotImplementedError


def is_label_deterministic(TS):
    raise NotImplementedError

עליכם לממש את המטלה בשפת Python.

TS היא מערכת מעברים המיוצגת ע"י מילון בפורמט הבא:

TS = {
    "S": {"s1", "s2", "s3"},
    "I": {"s1"},
    "Act": {"a", "b", "c"},
    "to": {("s1", "a", "s2"), ("s1", "a", "s1"), ("s1", "b", "s2"),
           ("s2", "c", "s3"), ("s3", "c", "s1")},
    "AP": {"p", "q"},
    "L": lambda s: {"p"} if s == "s1" else {"p", "q"} if s == "s2" else {}
}
C היא קבוצה של מצבים.

a היא פעולה.

דוגמה:

assert post(TS, "s1", "a") == {"s1", "s2"}
assert post(TS, {"s1", "s2"}, "a") == {"s1", "s2"}
assert pre(TS, {"s1", "s2"}) == {"s1", "s3"}
assert pre(TS, "s1") == {"s1", "s3"}
assert not is_action_deterministic(TS)
assert is_label_deterministic(TS)
