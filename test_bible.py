import typing as t
from textwrap import dedent
from unittest import TestCase

from bible import (
    BOOKS,
    REVERSE_LOOKUP,
    REVERSE_LOOKUP_NO_VOWELS,
    SPECIAL_ABBREVATIONS,
    Book,
    BookNotFound,
    Verse,
    parse_chapters_with_verses,
    parse_query,
    parse_single_chapter_no_verse,
    parse_single_chapter_with_start_verse,
    parse_single_chapter_with_verses,
    process,
    verse_to_markdown,
)


class TestBook(TestCase):
    def test_get_book_found(self):
        books = [
            ("1", "Genesis"),
            ("53", "2 Thessalonians"),
            ("66", "Revelation"),
            ("Genesis", "Genesis"),
            ("2 Thessalonians", "2 Thessalonians"),
            ("2thessalonians", "2 Thessalonians"),
            ("2th", "2 Thessalonians"),
            ("pm", "Philemon"),
            ("pp", "Philippians"),
            ("php", "Philippians"),
            ("lk", "Luke"),
            ("jhn", "John"),
            ("sa", "1 Samuel"),
            ("sm", "1 Samuel"),
            ("el", "1 Samuel"),
            ("s m", "1 Samuel"),
            ("gt", "Galatians"),
            ("ec", "Ecclesiastes"),
        ]
        for string, book in books:
            with self.subTest():
                self.assertEqual(Book.get_book(string).name, book)

    def test_get_book_not_found(self):
        with self.assertRaises(BookNotFound):
            Book.get_book("bar")

    def test_special_abbrevations(self):
        for book in SPECIAL_ABBREVATIONS.values():
            with self.subTest():
                self.assertIn(book, [b[0] for b in BOOKS.values()])

    def _find_dups(self, length: int) -> t.List[t.Tuple[str, str]]:
        names = [key for key in REVERSE_LOOKUP.keys()]
        abbr_names = [(name[:length], name) for name in names]
        abbrs = [name[:length] for name in names]
        dups = []
        for i, abbr in enumerate(abbrs):
            if abbrs.count(abbr) > 1:
                dups.append(abbr_names[i])
        return sorted(list(dups))

    def test_2_initials(self):
        dups = self._find_dups(2)
        print(f"duplicates for 2 initials: {dups}")
        self.assertEqual(len(dups), 26)

    def test_3_initials(self):
        dups = self._find_dups(3)
        print(f"duplicates for 3 initials: {dups}")
        self.assertEqual(len(dups), 4)

    def test_4_initials(self):
        dups = self._find_dups(4)
        print(f"duplicates for 4 initials: {dups}")
        self.assertEqual(len(dups), 2)

    def test_5_initials(self):
        dups = self._find_dups(5)
        self.assertEqual(len(dups), 0)

    def test_reverse_lookup_no_vowels_no_dups(self):
        assert len(REVERSE_LOOKUP_NO_VOWELS) == len(BOOKS)

    def test_reverse_lookup_no_vowels_no_overlap(self):
        assert (
            set(REVERSE_LOOKUP_NO_VOWELS.keys()) & SPECIAL_ABBREVATIONS.keys() == set()
        )


class TestVerse(TestCase):
    def test_to_markdown(self):
        verses = [
            (
                1,
                "After this there was a feast of the Jews, and Jesus went up to Jerusalem.",
                """
                1. After this there was a feast of the Jews,
                    and Jesus went up to Jerusalem.
                """,
            ),
            (
                6,
                'When Jesus saw him lying there and knew that he had already been there a long time, he said to him, "Do you want to be healed?"',
                """
                6. When Jesus saw him lying there and knew that he had already been there a long time,
                    he said to him,
                    "Do you want to be healed?"
                """,
            ),
            (
                9,
                "And at once the man was healed, and he took up his bed and walked. Now that day was the Sabbath.",
                """
                9. And at once the man was healed,
                    and he took up his bed and walked.
                    Now that day was the Sabbath.
                """,
            ),
            (
                21,
                'And they asked him, "What then? Are you Elijah?" He said, "I am not." "Are you the Prophet?" And he answered, "No."',
                """
                21. And they asked him,
                    "What then?
                    Are you Elijah?"
                    He said,
                    "I am not."
                    "Are you the Prophet?"
                    And he answered,
                    "No."
                """,
            ),
            (
                42,
                'He brought him to Jesus. Jesus looked at him and said, "You are Simon the son of John. You shall be called Cephas" (which means Peter(12)).',
                """
                42. He brought him to Jesus.
                    Jesus looked at him and said,
                    "You are Simon the son of John.
                    You shall be called Cephas"
                    (which means Peter(12)).
                """,
            ),
            (
                4,
                'Nicodemus said to him, "How can a man be born when he is old? Can he enter a second time into his mother\'s womb and be born?"',
                """
                4. Nicodemus said to him,
                    "How can a man be born when he is old?
                    Can he enter a second time into his mother's womb and be born?"
                """,
            ),
            (
                25,
                'Jesus said to her, "I am the resurrection and the life.(4) Whoever believes in me, though he die, yet shall he live,',
                """
                25. Jesus said to her,
                    "I am the resurrection and the life.(4)
                    Whoever believes in me, though he die, yet shall he live,
                """,
            ),
            (
                14,
                "so that in Christ Jesus the blessing of Abraham might come to the Gentiles, so that we might receive the promised Spirit(5) through faith.",
                """
                14. so that in Christ Jesus the blessing of Abraham might come to the Gentiles,
                    so that we might receive the promised Spirit(5) through faith.
                """,
            ),
            (
                8,
                'The wind(5) blows where it wishes, and you hear its sound, but you do not know where it comes from or where it goes. So it is with everyone who is born of the Spirit."',
                """
                8. The wind(5) blows where it wishes,
                    and you hear its sound,
                    but you do not know where it comes from or where it goes.
                    So it is with everyone who is born of the Spirit."
                """,
            ),
            (
                27,
                "And he has given him authority to execute judgment, because he is the Son of Man.",
                """
                27. And he has given him authority to execute judgment,
                    because he is the Son of Man.
                """,
            ),
            (
                15,
                "If you were of the world, the world would love you as its own; but because you are not of the world, but I chose you out of the world, therefore the world hates you.",
                """
                15. If you were of the world, the world would love you as its own;
                    but because you are not of the world,
                    but I chose you out of the world,
                    therefore the world hates you.
                """,
            ),
            (
                25,
                "and needed no one to bear witness about man, for he himself knew what was in man.",
                """
            25. and needed no one to bear witness about man,
                for he himself knew what was in man.
            """,
            ),
            (
                5,
                "I have oxen, donkeys, flocks, male servants, and female servants. I have sent to tell my lord, in order that I may find favor in your sight.'\"",
                """
                5. I have oxen, donkeys, flocks, male servants, and female servants.
                    I have sent to tell my lord,
                    in order that I may find favor in your sight.'"
                """,
            ),
            (
                22,
                "If I had not come and spoken to them, they would not have been guilty of sin,(2) but now they have no excuse for their sin.",
                """
                22. If I had not come and spoken to them, they would not have been guilty of sin,(2)
                    but now they have no excuse for their sin.
                """,
            ),
            (
                20,
                "Remember the word that I said to you: 'A servant is not greater than his master.' If they persecuted me, they will also persecute you. If they kept my word, they will also keep yours.",
                """
                20. Remember the word that I said to you:
                    'A servant is not greater than his master.'
                    If they persecuted me, they will also persecute you.
                    If they kept my word, they will also keep yours.
                """,
            ),
            (
                30,
                "How could one have chased a thousand, and two have put ten thousand to flight, unless their Rock had sold them, and the LORD had given them up?",
                """
                30. How could one have chased a thousand,
                    and two have put ten thousand to flight,
                    unless their Rock had sold them,
                    and the LORD had given them up?
                """,
            ),
            (
                4,
                "So Abram went, as the LORD had told him, and Lot went with him. Abram was seventy-five years old when he departed from Haran.",
                """
                4. So Abram went,
                    as the LORD had told him,
                    and Lot went with him.
                    Abram was seventy-five years old when he departed from Haran.
                """,
            ),
            (
                10,
                "and with every living creature that is with you, the birds, the livestock, and every beast of the earth with you, as many as came out of the ark; it is for every beast of the earth.",
                """
                10. and with every living creature that is with you, the birds, the livestock,
                    and every beast of the earth with you, as many as came out of the ark;
                    it is for every beast of the earth.
                """,
            ),
            (
                22,
                "The sons of Shem: Elam, Asshur, Arpachshad, Lud, and Aram.",
                """
                22. The sons of Shem:
                    Elam, Asshur, Arpachshad, Lud, and Aram.
                """,
            ),
            (
                29,
                "Ophir, Havilah, and Jobab; all these were the sons of Joktan.",
                """
                29. Ophir, Havilah, and Jobab;
                    all these were the sons of Joktan.
                """,
            ),
            (
                6,
                "He said this, not because he cared about the poor, but because he was a thief, and having charge of the moneybag he used to help himself to what was put into it.",
                """
                6. He said this,
                    not because he cared about the poor,
                    but because he was a thief,
                    and having charge of the moneybag he used to help himself to what was put into it.
                """,
            ),
            (
                9,
                "When the large crowd of the Jews learned that Jesus(4) was there, they came, not only on account of him but also to see Lazarus, whom he had raised from the dead.",
                """
                9. When the large crowd of the Jews learned that Jesus(4) was there, they came,
                    not only on account of him but also to see Lazarus,
                    whom he had raised from the dead.
                """,
            ),
            (
                31,
                "Now is the judgment of this world; now will the ruler of this world be cast out.",
                """
                31. Now is the judgment of this world;
                    now will the ruler of this world be cast out.
                """,
            ),
            (
                7,
                "Nevertheless, I tell you the truth: it is to your advantage that I go away, for if I do not go away, the Helper will not come to you. But if I go, I will send him to you.",
                """
                7. Nevertheless, I tell you the truth:
                    it is to your advantage that I go away,
                    for if I do not go away, the Helper will not come to you.
                    But if I go, I will send him to you.
                """,
            ),
            (
                9,
                "The true light, which gives light to everyone, was coming into the world.",
                """
                9. The true light,
                    which gives light to everyone, was coming into the world.
                """,
            ),
            (
                38,
                "He set the sticks that he had peeled in front of the flocks in the troughs, that is, the watering places, where the flocks came to drink. And since they bred when they came to drink,",
                """
                38. He set the sticks that he had peeled in front of the flocks in the troughs, that is, the watering places,
                    where the flocks came to drink.
                    And since they bred when they came to drink,
             """,
            ),
            (
                19,
                'And this is the testimony of John, when the Jews sent priests and Levites from Jerusalem to ask him, "Who are you?"',
                """
                19. And this is the testimony of John,
                    when the Jews sent priests and Levites from Jerusalem to ask him,
                    "Who are you?"
                """,
            ),
            (
                12,
                "But to all who did receive him, who believed in his name, he gave the right to become children of God,",
                """
                12. But to all who did receive him,
                    who believed in his name, he gave the right to become children of God,
                """,
            ),
            (
                24,
                "Moreover, his concubine, whose name was Reumah, bore Tebah, Gaham, Tahash, and Maacah.",
                """
                24. Moreover, his concubine,
                    whose name was Reumah, bore Tebah, Gaham, Tahash, and Maacah.
                """,
            ),
            (
                15,
                "And Hagar bore Abram a son, and Abram called the name of his son, whom Hagar bore, Ishmael.",
                """
                15. And Hagar bore Abram a son,
                    and Abram called the name of his son,
                    whom Hagar bore, Ishmael.
                """,
            ),
            (
                1,
                'Now Boaz had gone up to the gate and sat down there. And behold, the redeemer, of whom Boaz had spoken, came by. So Boaz said, "Turn aside, friend; sit down here." And he turned aside and sat down.',
                """
                1. Now Boaz had gone up to the gate and sat down there.
                    And behold, the redeemer,
                    of whom Boaz had spoken, came by.
                    So Boaz said,
                    "Turn aside, friend;
                    sit down here."
                    And he turned aside and sat down.
                """,
            ),
            (
                38,
                "The cattle were 36,000, of which the LORD’s tribute was 72.",
                """
                38. The cattle were 36,000,
                    of which the LORD’s tribute was 72.
                """,
            ),
            (
                24,
                "(Now they had been sent from the Pharisees.)",
                """
                24. (Now they had been sent from the Pharisees.)
                """,
            ),
            (
                19,
                "who sets his heart to seek God, the LORD, the God of his fathers, even though not according to the sanctuary's rules of cleanness.\"",
                """
                19. who sets his heart to seek God, the LORD, the God of his fathers,
                    even though not according to the sanctuary's rules of cleanness."
                """,
            ),
            (
                5,
                'They answered him, "Jesus of Nazareth." Jesus said to them, "I am he."(1) Judas, who betrayed him, was standing with them.',
                """
                5. They answered him,
                    "Jesus of Nazareth."
                    Jesus said to them,
                    "I am he."(1)
                    Judas,
                    who betrayed him, was standing with them.
                """,
            ),
            (
                29,
                "A jar full of sour wine stood there, so they put a sponge full of the sour wine on a hyssop branch and held it to his mouth.",
                """
                29. A jar full of sour wine stood there,
                    so they put a sponge full of the sour wine on a hyssop branch and held it to his mouth.
                """,
            ),
            (
                26,
                'When Jesus saw his mother and the disciple whom he loved standing nearby, he said to his mother, "Woman, behold, your son!"',
                """
                26. When Jesus saw his mother and the disciple whom he loved standing nearby,
                    he said to his mother,
                    "Woman, behold, your son!"
                """,
            ),
            (
                33,
                "But when they came to Jesus and saw that he was already dead, they did not break his legs.",
                """
                33. But when they came to Jesus and saw that he was already dead,
                    they did not break his legs.
                """,
            ),
            (
                13,
                "So when Pilate heard these words, he brought Jesus out and sat down on the judgment seat at a place called The Stone Pavement, and in Aramaic(2) Gabbatha.",
                """
                13. So when Pilate heard these words,
                    he brought Jesus out and sat down on the judgment seat at a place called The Stone Pavement,
                    and in Aramaic(2) Gabbatha.
                """,
            ),
            (
                8,
                "If she does not please her master, who has designated her for himself, then he shall let her be redeemed. He shall have no right to sell her to a foreign people, since he has broken faith with her.",
                """
                8. If she does not please her master,
                    who has designated her for himself, then he shall let her be redeemed.
                    He shall have no right to sell her to a foreign people,
                    since he has broken faith with her.
                """,
            ),
            (
                37,
                "sold a field that belonged to him and brought the money and laid it at the apostles' feet.",
                """
                37. sold a field that belonged to him and brought the money and laid it at the apostles' feet.
                """,
            ),
        ]
        for number, text, result in verses:
            with self.subTest():
                self.assertEqual(
                    verse_to_markdown(number=number, text=text), dedent(result).strip()
                )


class TestParseQuery(TestCase):
    def test_parse_single_chapter_no_verse(self):
        for query, result in [
            ("", ("1", 1)),
            ("g1", ("g", 1)),
            ("1cor2", ("1cor", 2)),
            ("111", ("1", 11)),
            ("1j", ("1j", 1)),
            ("ob1", ("ob", 1)),
        ]:
            with self.subTest():
                assert parse_single_chapter_no_verse(query) == result

    def test_parse_single_chapter_with_start_verse(self):
        for query, result in [
            ("g1:1", ("g", 1, 1)),
            ("g1v1", ("g", 1, 1)),
            ("g1:12", ("g", 1, 12)),
            ("g1v12", ("g", 1, 12)),
            ("1cor2:11", ("1cor", 2, 11)),
            ("1cor2v11", ("1cor", 2, 11)),
        ]:
            with self.subTest():
                assert parse_single_chapter_with_start_verse(query) == result

    def test_parse_single_chapter_with_verses(self):
        for query, result in [
            ("g1:1-20", ("g", 1, 1, 20)),
            ("g1:1–20", ("g", 1, 1, 20)),
            ("g1v1-20", ("g", 1, 1, 20)),
            ("g1:12-24", ("g", 1, 12, 24)),
            ("g1:12–24", ("g", 1, 12, 24)),
            ("g1v12-24", ("g", 1, 12, 24)),
            ("1cor2:11-13", ("1cor", 2, 11, 13)),
            ("1cor2v11-13", ("1cor", 2, 11, 13)),
        ]:
            with self.subTest():
                assert parse_single_chapter_with_verses(query) == result

    def test_parse_chapters_with_verses(self):
        for query, result in [
            ("g1:1-2:10", ("g", 1, 1, 2, 10)),
            ("g1:1–2:10", ("g", 1, 1, 2, 10)),
            ("g1v1-2:10", ("g", 1, 1, 2, 10)),
            ("g1:12-2:24", ("g", 1, 12, 2, 24)),
            ("g1v12-2:24", ("g", 1, 12, 2, 24)),
            ("1john1-2:10", ("1john", 1, 0, 2, 10)),
            ("1john1-2v10", ("1john", 1, 0, 2, 10)),
            ("1john1-2", ("1john", 1, 0, 2, 0)),
            ("1cor2:11-4:13", ("1cor", 2, 11, 4, 13)),
            ("1cor2v11-4v13", ("1cor", 2, 11, 4, 13)),
            ("1cor12-13:11", ("1cor", 12, 0, 13, 11)),
            ("1cor12-13v11", ("1cor", 12, 0, 13, 11)),
        ]:
            with self.subTest():
                assert parse_chapters_with_verses(query) == result

    def test_parse_query(self):
        for query in [("1cor2:11-13"), ("1cor2v11-13")]:
            with self.subTest():
                self.assertEqual(
                    parse_query(query),
                    (
                        Verse(book=Book.get_book("1cor"), chapter_number=2, number=11),
                        Verse(book=Book.get_book("1cor"), chapter_number=2, number=13),
                    ),
                )


class TestProcess(TestCase):
    def test_process_not_strict(self):
        cases = [
            # 0. ordinary verse
            (
                """
John 15:18

The Hatred of the World

  [18] “If the world hates you, know that it has hated me before it hated you. (ESV)
""",
                """
# John 15:18

---

## The Hatred of the World


18. "If the world hates you, know that it has hated me before it hated you.
    (ESV)
""",
            ),
            # 1. multi-line verse
            (
                """
John 12:15-16

    [15] “Fear not, daughter of Zion;
    behold, your king is coming,
        sitting on a donkey’s colt!”


      [16] His disciples did not understand these things at first, but when Jesus was glorified, then they remembered that these things had been written about him and had been done to him. (ESV)
                """,
                """
# John 12:15-16


15. "Fear not, daughter of Zion;
    behold, your king is coming,
        sitting on a donkey's colt!"


16. His disciples did not understand these things at first,
    but when Jesus was glorified, then they remembered that these things had been written about him and had been done to him.
    (ESV)
                """,
            ),
            # 2. header within verse and 2nd part no need of breaking
            (
                """
John 12:36

  [36] While you have the light, believe in the light, that you may become sons of light.”

The Unbelief of the People

  When Jesus had said these things, he departed and hid himself from them. (ESV)
""",
                """
# John 12:36

---


36. While you have the light, believe in the light, that you may become sons of light."


---

## The Unbelief of the People

  When Jesus had said these things,
    he departed and hid himself from them.
    (ESV)
""",
            ),
            # 3. header within verse and 2nd part needs breaking
            (
                """
John 16:4

  [4] But I have said these things to you, that when their hour comes you may remember that I told them to you.

The Work of the Holy Spirit

  “I did not say these things to you from the beginning, because I was with you. (ESV)
""",
                """
# John 16:4

---


4. But I have said these things to you, that when their hour comes you may remember that I told them to you.


---

## The Work of the Holy Spirit

  "I did not say these things to you from the beginning,
    because I was with you.
    (ESV)
""",
            ),
            # 4. quote of scripture within verse
            (
                """
John 19:24

  [24] so they said to one another, “Let us not tear it, but cast lots for it to see whose it shall be.” This was to fulfill the Scripture which says,

    “They divided my garments among them,
        and for my clothing they cast lots.”


      So the soldiers did these things, (ESV)
                """,
                """
# John 19:24

---


24. so they said to one another,
    "Let us not tear it,
    but cast lots for it to see whose it shall be."
    This was to fulfill the Scripture which says,


    "They divided my garments among them,
        and for my clothing they cast lots."

      So the soldiers did these things, (ESV)
                """,
            ),
            # 5. missing a verse
            (
                """
John 5:3–5

  [3] In these lay a multitude of invalids—blind, lame, and paralyzed.(1) [5] One man was there who had been an invalid for thirty-eight years.

Footnotes

(1) 5:3 Some manuscripts insert, wholly or in part, *waiting for the moving of the water; [4] for an angel of the Lord went down at certain seasons into the pool, and stirred the water: whoever stepped in first after the stirring of the water was healed of whatever disease he had*
 (ESV)
                """,
                """
# John 5:3–5

---


3. In these lay a multitude of invalids—blind, lame, and paralyzed.(1)


4.  


5. One man was there who had been an invalid for thirty-eight years.


---

## Footnotes
- (1) 5:3 Some manuscripts insert, wholly or in part, *waiting for the moving of the water; [4] for an angel of the Lord went down at certain seasons into the pool, and stirred the water: whoever stepped in first after the stirring of the water was healed of whatever disease he had*
 (ESV)
                """,
            ),
            # 6. paragraph starting from the middle of a verse
            (
                """
John 5:8–10

  [8] Jesus said to him, “Get up, take up your bed, and walk.” [9] And at once the man was healed, and he took up his bed and walked.

  Now that day was the Sabbath. [10] So the Jews(1) said to the man who had been healed, “It is the Sabbath, and it is not lawful for you to take up your bed.”

Footnotes

(1) 5:10 The Greek word *Ioudaioi* refers specifically here to Jewish religious leaders, and others under their influence, who opposed Jesus in that time; also verses 15, 16, 18
 (ESV)
                """,
                """
# John 5:8–10

---


8. Jesus said to him,
    "Get up, take up your bed, and walk."


9. And at once the man was healed,
    and he took up his bed and walked.


---

  Now that day was the Sabbath.


10. So the Jews(1) said to the man who had been healed,
    "It is the Sabbath,
    and it is not lawful for you to take up your bed."


---

## Footnotes
- (1) 5:10 The Greek word *Ioudaioi* refers specifically here to Jewish religious leaders, and others under their influence, who opposed Jesus in that time; also verses 15, 16, 18
 (ESV)
                """,
            ),
            # 7. chapter starts from middle of line
            (
                """
John 7:52–8:2

  [52] They replied, “Are you from Galilee too? Search and see that no prophet arises from Galilee.”

[The earliest manuscripts do not include 7:53–8:11.](1)

The Woman Caught in Adultery

  [53] [[They went each to his own house, [1] but Jesus went to the Mount of Olives. [2] Early in the morning he came again to the temple. All the people came to him, and he sat down and taught them.

Footnotes

(1) 7:53 Some manuscripts do not include 7:53–8:11; others add the passage here or after 7:36 or after 21:25 or after Luke 21:38, with variations in the text
 (ESV)
                """,
                """
# John 7:52–8:2

---


52. They replied,
    "Are you from Galilee too?
    Search and see that no prophet arises from Galilee."


---

## [The earliest manuscripts do not include 7:53–8:11.](1)
---

## The Woman Caught in Adultery


53. [[They went each to his own house,


1. but Jesus went to the Mount of Olives.


2. Early in the morning he came again to the temple.
    All the people came to him,
    and he sat down and taught them.


---

## Footnotes
- (1) 7:53 Some manuscripts do not include 7:53–8:11; others add the passage here or after 7:36 or after 21:25 or after Luke 21:38, with variations in the text
 (ESV)
                """,
            ),
            # 8. chapter number
            (
                """
John 15:27–16:1

  [27] And you also will bear witness, because you have been with me from the beginning.

  [1] “I have said all these things to you to keep you from falling away. (ESV)
""",
                """
# John 15:27–16:1

---


27. And you also will bear witness,
    because you have been with me from the beginning.


---


1. "I have said all these things to you to keep you from falling away.
    (ESV)
                """,
            ),
        ]
        edit = lambda s: dedent(s.lstrip("\n").rstrip())  # noqa: E731
        for text, expected in cases[:]:
            print(process(edit(text)))
            with self.subTest():
                self.assertEqual(process(edit(text)), dedent(edit(expected)))

    def test_process_strict(self):
        cases = [
            # 0. verse over multi lines
            (
                """
John 12:15

    [15] “Fear not, daughter of Zion;
    behold, your king is coming,
        sitting on a donkey’s colt!” (ESV)
""",
                """
# John 12:15


15. "Fear not, daughter of Zion;<br> behold, your king is coming,<br> sitting on a donkey's colt!"<br> (ESV)
""",
            ),
            # 1. header in between a verse
            (
                """
Obadiah 1



  [1] The vision of Obadiah.

Edom Will Be Humbled

    Thus says the Lord GOD concerning Edom:
    We have heard a report from the LORD,
        and a messenger has been sent among the nations:
    “Rise up! Let us rise against her for battle!” (ESV)
                """,
                """
# Obadiah 1

---


1. The vision of Obadiah.


---

## Edom Will Be Humbled


Thus says the Lord GOD concerning Edom:<br> We have heard a report from the LORD,<br> and a messenger has been sent among the nations:<br> "Rise up!<br> Let us rise against her for battle!"<br> (ESV)
                """,
            ),
        ]
        edit = lambda s: dedent(s.lstrip("\n").rstrip())  # noqa: E731
        for text, expected in cases[:]:
            # print(process(edit(text)))
            with self.subTest():
                self.assertEqual(
                    process(edit(text), strict=True), dedent(edit(expected))
                )
