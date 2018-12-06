import connection


@connection.connection_handler
def get_all_questions(cursor, first_attribute='', second_attribute=''):
    attributes = ['submission_time-DESC', 'submission_time-ASC', 'view_number-DESC',
                  'view_number-ASC', 'vote_number-DESC', 'vote_number-ASC', 'title-DESC', 'title-ASC', '']
    if first_attribute in attributes and second_attribute in attributes:

            SQL_part = 'ORDER BY' if first_attribute or second_attribute else ''
            comma = ', ' if first_attribute and second_attribute else ''
            first_attribute = first_attribute.replace('-', ' ')
            second_attribute = second_attribute.replace('-', ' ')

            cursor.execute(f"""
                            SELECT * FROM question
                            {SQL_part} {first_attribute}{comma}{second_attribute};
                            """)
            return cursor.fetchall()
    else:
        return 'That is not an option.'


@connection.connection_handler
def get_question_by_id(cursor, question_id):
    cursor.execute("""
                    SELECT * FROM question
                    WHERE id = %(question_id)s
                    """,
                   {'question_id': question_id})
    return cursor.fetchone()


@connection.connection_handler
def get_answer_by_id(cursor, answer_id):
    cursor.execute("""
                    SELECT * FROM answer
                    WHERE id = %(answer_id)s
                    """,
                   {'answer_id': answer_id})
    return cursor.fetchone()


@connection.connection_handler
def get_all_answers(cursor):
    cursor.execute("""
                    SELECT * FROM answer
                    """)
    return cursor.fetchall()

@connection.connection_handler
def get_answers_for_question(cursor, question_id):
    cursor.execute("""
                    SELECT * FROM answer
                    WHERE question_id = %(question_id)s
                    ORDER BY submission_time DESC
                    """,
                   {'question_id': question_id})

    return cursor.fetchall()


@connection.connection_handler
def save_new_question(cursor, new_question):
    cursor.execute("""
                    INSERT INTO question
                    (title, message, image)
                    VALUES(%(title)s, %(message)s, %(image)s)
                    RETURNING id
                    """,
                    new_question)

    return cursor.fetchone()['id']


@connection.connection_handler
def save_new_answer(cursor, new_answer, question_id):
    new_answer['question_id'] = question_id
    cursor.execute("""
                    INSERT INTO answer
                    (question_id, message, image)
                    VALUES(%(question_id)s, %(message)s, %(image)s)
                    """,
                   new_answer)


@connection.connection_handler
def update_question(cursor, updated_question):
    cursor.execute("""
                    UPDATE question
                    SET title = %(title)s, message = %(message)s, image = %(image)s
                    WHERE id = %(id)s
                    """,
                   updated_question)


@connection.connection_handler
def delete_answer(cursor, answer_id):
    cursor.execute("""
                    DELETE FROM answer
                    WHERE id = %(answer_id)s
                    """,
                   {"answer_id": answer_id})


@connection.connection_handler
def delete_question_with_answers(cursor, question_id):
    cursor.execute("""
                    DELETE FROM question
                    WHERE id = %(question_id)s
                    """,
                   {"question_id": question_id})


@connection.connection_handler
def change_vote(cursor, type, id, change=0):
    cursor.execute("""
                    UPDATE {}
                    SET vote_number = vote_number + %(change)s
                    WHERE id = %(id)s
                    """.format(type if type in ['answer', 'question'] else ''),
                   {'id': id,
                    'change': change})

@connection.connection_handler
def add_comment(cursor, new_comment):
    cursor.execute("""
                    INSERT INTO comment
                    (question_id, answer_id, message) 
                    VALUES (%(question_id)s, %(answer_id)s, %(message)s)
                    """,
                   new_comment)

@connection.connection_handler
def get_comments(cursor, id):
    cursor.execute("""
                    SELECT * FROM comment
                    WHERE question_id = %(id)s AND answer_id IS NULL
                    ORDER BY submission_time DESC
                    """,
                   {"id": id})
    return cursor.fetchall()

@connection.connection_handler
def get_filtered_questions(cursor, filter):
    cursor.execute("""
                    SELECT DISTINCT question.* FROM question
                    LEFT JOIN answer ON question.id=answer.question_id
                    WHERE LOWER(question.message) LIKE LOWER(%(word)s)
                    OR LOWER(question.title) LIKE LOWER(%(word)s)
                    OR LOWER(answer.message) LIKE LOWER(%(word)s)
                    ;
                """,
                filter)
    return cursor.fetchall()


@connection.connection_handler
def update_answer(cursor, updated_question):
    cursor.execute("""
                    UPDATE answer
                    SET message = %(message)s, image = %(image)s
                    WHERE id = %(id)s
                    """,
                   updated_question)


@connection.connection_handler
def get_comments_for_answers(cursor, question_id):
    '''Returns a dictionary with keys as answer_id, each value is a list which contain all comments (as dictionaris) related to the key answer_id'''
    cursor.execute("""
                    SELECT message, submission_time, answer_id, id, edited_count
                    FROM comment
                    WHERE question_id = %(question_id)s
                    ORDER BY submission_time DESC
                    """,
                   {'question_id': question_id})
    comments =  cursor.fetchall()
    answer_id_sorted_comments = {}
    for comment in comments:
        key = str(comment['answer_id'])
        del comment['answer_id']
        if key not in answer_id_sorted_comments:
            answer_id_sorted_comments[key] = [comment]
        else:
            pass
            answer_id_sorted_comments[key] += [comment]

    return answer_id_sorted_comments


@connection.connection_handler
def get_comment_by_id(cursor, id):
    cursor.execute("""
                    SELECT id, question_id, message FROM comment
                    WHERE id = %(id)s
                    """,
                   {"id": id})
    return cursor.fetchone()


@connection.connection_handler
def update_comment(cursor, updated_comment):
    cursor.execute("""
                    UPDATE comment
                    SET message = %(message)s, edited_count = edited_count + 1, submission_time = now()
                    WHERE id = %(id)s
                    """,
                   updated_comment)
