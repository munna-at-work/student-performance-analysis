# Student Performance Analysis System
# Course: Computational Thinking and Programming (2026CSAE100)
# Data is stored in students.csv, reports are saved as .txt files

import csv
import os
from datetime import datetime

DATA_FILE = "students.csv"
SUBJECTS = ("Maths", "Physics", "Chemistry", "English", "Python")
PASS_MARK = 40

# grade boundaries as (minimum percentage, grade)
GRADE_TABLE = [(90, "A+"), (80, "A"), (70, "B+"), (60, "B"), (50, "C"), (40, "D"), (0, "F")]


# ---------------- File handling ----------------

def load_data():
    """Read all student records from the CSV file into a dictionary."""
    students = {}
    if not os.path.exists(DATA_FILE):
        return students
    with open(DATA_FILE, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                marks = {sub: int(row[sub]) for sub in SUBJECTS}
            except (ValueError, KeyError):
                print("Skipping bad row for roll no:", row.get("Roll"))
                continue
            students[row["Roll"]] = {"name": row["Name"], "marks": marks}
    return students


def save_data(students):
    """Write all student records back to the CSV file."""
    with open(DATA_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Roll", "Name"] + list(SUBJECTS))
        for roll, info in students.items():
            row = [roll, info["name"]] + [info["marks"][s] for s in SUBJECTS]
            writer.writerow(row)


# ---------------- Input helpers ----------------

def read_marks(subject):
    """Keep asking until a valid mark between 0 and 100 is entered."""
    while True:
        value = input(f"  Marks in {subject} (0-100): ").strip()
        if not value.isdigit():
            print("  Invalid input. Please enter a whole number.")
            continue
        mark = int(value)
        if 0 <= mark <= 100:
            return mark
        print("  Marks must be between 0 and 100.")


def read_roll():
    roll = input("Enter roll number: ").strip().upper()
    if roll == "" or not roll.isalnum():
        print("Roll number should contain only letters and digits.")
        return None
    return roll


def read_name():
    name = input("Enter student name: ").strip().title()
    if name == "" or not name.replace(" ", "").isalpha():
        print("Name should contain only letters.")
        return None
    return name


# ---------------- Calculations ----------------

def total_marks(marks):
    return sum(marks.values())


def percentage(marks):
    return round(total_marks(marks) / len(SUBJECTS), 2)


def get_grade(percent):
    for limit, grade in GRADE_TABLE:
        if percent >= limit:
            return grade
    return "F"


def failed_subjects(marks):
    return [sub for sub, m in marks.items() if m < PASS_MARK]


def result_status(marks):
    if failed_subjects(marks):
        return "FAIL"
    return "PASS"


def rank_students(students):
    """Return a list of (roll, name, percentage) sorted from highest to lowest."""
    ranking = []
    for roll, info in students.items():
        ranking.append((roll, info["name"], percentage(info["marks"])))
    ranking.sort(key=lambda item: item[2], reverse=True)
    return ranking


def subject_statistics(students):
    """Average, highest and lowest marks for each subject."""
    stats = {}
    for sub in SUBJECTS:
        scores = [info["marks"][sub] for info in students.values()]
        stats[sub] = {
            "avg": round(sum(scores) / len(scores), 2),
            "high": max(scores),
            "low": min(scores),
            "fail": sum(1 for s in scores if s < PASS_MARK),
        }
    return stats


def weak_subjects_of_student(marks):
    """Subjects where the student is below their own average by 10 or more marks."""
    avg = percentage(marks)
    return [sub for sub, m in marks.items() if avg - m >= 10]


def weakest_class_subject(stats):
    return min(stats, key=lambda sub: stats[sub]["avg"])


def grade_distribution(students):
    dist = {grade: 0 for _, grade in GRADE_TABLE}
    for info in students.values():
        dist[get_grade(percentage(info["marks"]))] += 1
    return dist


# ---------------- Menu features ----------------

def add_student(students):
    roll = read_roll()
    if roll is None:
        return
    if roll in students:
        print("A student with this roll number already exists.")
        return
    name = read_name()
    if name is None:
        return
    marks = {}
    for sub in SUBJECTS:
        marks[sub] = read_marks(sub)
    students[roll] = {"name": name, "marks": marks}
    save_data(students)
    print(f"Record of {name} saved successfully.")


def update_marks(students):
    roll = read_roll()
    if roll not in students:
        print("Roll number not found.")
        return
    print("Subjects:", ", ".join(SUBJECTS))
    sub = input("Which subject to update? ").strip().title()
    if sub not in SUBJECTS:
        print("Invalid subject name.")
        return
    students[roll]["marks"][sub] = read_marks(sub)
    save_data(students)
    print("Marks updated.")


def delete_student(students):
    roll = read_roll()
    if roll not in students:
        print("Roll number not found.")
        return
    confirm = input(f"Delete {students[roll]['name']}? (y/n): ").strip().lower()
    if confirm == "y":
        del students[roll]
        save_data(students)
        print("Record deleted.")
    else:
        print("Delete cancelled.")


def show_all(students):
    if not students:
        print("No records found.")
        return
    header = f"{'Roll':<8}{'Name':<18}" + "".join(f"{s[:5]:>7}" for s in SUBJECTS)
    header += f"{'Total':>7}{'%':>8}{'Grade':>7}"
    print(header)
    print("-" * len(header))
    for roll, info in students.items():
        m = info["marks"]
        line = f"{roll:<8}{info['name']:<18}" + "".join(f"{m[s]:>7}" for s in SUBJECTS)
        p = percentage(m)
        line += f"{total_marks(m):>7}{p:>8}{get_grade(p):>7}"
        print(line)


def search_student(students):
    roll = read_roll()
    if roll not in students:
        print("Roll number not found.")
        return
    info = students[roll]
    m = info["marks"]
    p = percentage(m)
    print(f"\nName      : {info['name']}")
    print(f"Roll No   : {roll}")
    for sub in SUBJECTS:
        print(f"  {sub:<10}: {m[sub]}")
    print(f"Total     : {total_marks(m)} / {len(SUBJECTS) * 100}")
    print(f"Percentage: {p}%")
    print(f"Grade     : {get_grade(p)}")
    print(f"Result    : {result_status(m)}")
    failed = failed_subjects(m)
    if failed:
        print("Failed in :", ", ".join(failed))
    weak = weak_subjects_of_student(m)
    if weak:
        print("Needs improvement in:", ", ".join(weak))


def show_ranking(students):
    if not students:
        print("No records found.")
        return
    print(f"{'Rank':<6}{'Roll':<8}{'Name':<18}{'%':>8}")
    rank = 0
    last_percent = None
    for position, (roll, name, p) in enumerate(rank_students(students), start=1):
        if p != last_percent:   # same percentage gets the same rank
            rank = position
            last_percent = p
        print(f"{rank:<6}{roll:<8}{name:<18}{p:>8}")


def class_analysis(students):
    if not students:
        print("No records found.")
        return
    stats = subject_statistics(students)
    print(f"{'Subject':<12}{'Average':>9}{'Highest':>9}{'Lowest':>8}{'Failed':>8}")
    for sub, s in stats.items():
        print(f"{sub:<12}{s['avg']:>9}{s['high']:>9}{s['low']:>8}{s['fail']:>8}")

    ranking = rank_students(students)
    print("\nClass topper :", ranking[0][1], f"({ranking[0][2]}%)")
    print("Lowest score :", ranking[-1][1], f"({ranking[-1][2]}%)")
    print("Weakest subject of class:", weakest_class_subject(stats))

    passed = sum(1 for info in students.values() if result_status(info["marks"]) == "PASS")
    print(f"Pass percentage: {round(passed / len(students) * 100, 2)}%")

    print("\nGrade distribution:")
    for grade, count in grade_distribution(students).items():
        print(f"  {grade:<3}: {'*' * count} ({count})")


def generate_report(students):
    """Write a full class report into a text file."""
    if not students:
        print("No records found.")
        return
    stats = subject_statistics(students)
    ranking = rank_students(students)
    filename = "class_report_" + datetime.now().strftime("%Y%m%d_%H%M") + ".txt"
    with open(filename, "w") as f:
        f.write("CLASS PERFORMANCE REPORT\n")
        f.write("Generated on: " + datetime.now().strftime("%d-%m-%Y %H:%M") + "\n")
        f.write(f"Total students: {len(students)}\n\n")
        f.write("Subject-wise summary\n")
        for sub, s in stats.items():
            f.write(f"  {sub:<10} avg {s['avg']:<6} high {s['high']:<4} low {s['low']:<4} failed {s['fail']}\n")
        f.write("\nMerit list\n")
        for pos, (roll, name, p) in enumerate(ranking, start=1):
            f.write(f"  {pos}. {name} ({roll}) - {p}% - {get_grade(p)}\n")
        f.write("\nStudents needing attention\n")
        found = False
        for roll, info in students.items():
            failed = failed_subjects(info["marks"])
            if failed:
                found = True
                f.write(f"  {info['name']} ({roll}) failed in: {', '.join(failed)}\n")
        if not found:
            f.write("  None\n")
    print("Report saved as", filename)


def show_chart(students):
    """Bar chart of subject averages (needs matplotlib)."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib is not installed, chart cannot be shown.")
        return
    if not students:
        print("No records found.")
        return
    stats = subject_statistics(students)
    averages = [stats[s]["avg"] for s in SUBJECTS]
    plt.bar(SUBJECTS, averages)
    plt.title("Subject-wise Class Average")
    plt.ylabel("Average marks")
    plt.ylim(0, 100)
    plt.savefig("subject_average.png")
    print("Chart saved as subject_average.png")
    plt.show()


# ---------------- Main program ----------------

def main():
    students = load_data()
    menu = {
        "1": ("Add student", add_student),
        "2": ("Update marks", update_marks),
        "3": ("Delete student", delete_student),
        "4": ("Display all students", show_all),
        "5": ("Search student report card", search_student),
        "6": ("Show rank list", show_ranking),
        "7": ("Class analysis", class_analysis),
        "8": ("Generate text report", generate_report),
        "9": ("Show subject average chart", show_chart),
    }
    while True:
        print("\n===== STUDENT PERFORMANCE ANALYSIS SYSTEM =====")
        for key, (title, _) in menu.items():
            print(f"{key}. {title}")
        print("0. Exit")
        choice = input("Enter your choice: ").strip()
        if choice == "0":
            print("Thank you. Exiting program.")
            break
        if choice in menu:
            print()
            menu[choice][1](students)
        else:
            print("Invalid choice. Please select from the menu.")


if __name__ == "__main__":
    main()
