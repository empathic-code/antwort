Antwort
=======
Antwort is a DSL for questionnaires that I am using for my bachelor thesis.
The word "Antwort" is German for "answer". 

Motivation
----------
The first scientific study that I conducted included a couple of questionnaires. I created those by writing the HTML Code myself. This turned out to be tedious and error prone. I wanted to create a small language format, that would allow me to create questinnaires in an easy, visual way. 

Since I love python and markdown, the DSL picks up some of their concepts (visually and aesthetically, that is). 

I could have created this DSL in many different ways, yet I wanted to learn about writing compilers. I looked into "Language Implementation Patterns" by Terrence Parr, who is also the creator of Antlr. The implementation therefore contains some stuff such as support for speculative parsing, mark and rewind infrastructure in the parser, that is not strictly speaking necessary for what I'm doing. 

Feel free to comment on what I could have done better, I am always eager to learn. 

Specification
-------------
Antwort contains a list of questions. A Question usually looks like this:

    1. How old are you? (age) *
        Please specify your current age.
        [__ Age __] (0 - 100)

A Question has a Number and a title. After that there is an identifier, which names the variable for this question. The asterisk at the end tells you whether or not this question should be required.

In the next line after the question you can give some more context. This explanatory sentence is optional.

After that you define in what way the person should answer. In the example there is a textbox specified that has the word "Age" as a placeholder. After that there is a range defined, that converters can use for validation.

So far there is only a HTML generator that produces HTML 5. The code here is transformed to the following: 

    <div>
        <h2>1. Alter</h2>
        <blockquote>Please specify your current age.</blockquote>
        <input name="age" placeholder="Age" type="number" min="0" max="100" required>
    </div>

Answer Formats
--------------
There are different answer formats that the DSL will accept underneath a question. 
You can specify:
 - Checkboxes
 - Radio buttons
 - One-lined textboxes (string or number)
 - Text areas
 - Drop-Down Selection Lists
 - Value Matrices

### Checkboxes

    1. Would you like to receive our newsletter? (_)
        [ ] Yes, send me your newsletter! (receive_newsletter)
        [ ] I would like to receive Emails about new offers by a third party! (third_party)

    <div>
        <h2>1. Would you like to receive our newsletter?</h2>
        <input type="checkbox" name="receive_newsletter" value="" >Yes, send me your newsletter!
        <input type="checkbox" name="third_party" value="" >I would like to receive Emails about new offers by a third party!
    </div>

### Radio Buttons

    1. Are you male of female? (sex) *
        ( ) Male (m)
        ( ) Female (w)

    <div>
        <h2>1. Are you male of female?</h2>
        <input type="radio" name="sex" value="m" required>Male
        <input type="radio" name="sex" value="w" required>Female
    </div>
    
### Input fields
    1. Age (age) * 
        How old are you? 
        [__ Age __] (0-100)

    <div>
        <h2>1. Age</h2>
        <blockquote>How old are you?</blockquote>
        <input name="age" placeholder="Age" type="number" min="0" max="100" required>
    </div>

### Text Areas
    20. Comments (comments)
        Do you have comments or would you like to suggest improvements to our services?
        [__ Comments _________]
        [_____________________]
        [_____________________]

    <div>
        <h2>20. Comments</h2>
        <blockquote>Do you have comments or would you like to suggest improvements to our services?</blockquote>
        <textarea name="comments" placeholder="Comments" rows="3" ></textarea>
    </div>

Note how the rows show up visually - You actually have to put the amount of rows that you want to show. The width doesn't matter as long as you put underscores within brackets.

### Drop Down Selection Lists
    5. Country (country)
        Where are you from? 
        [
            Germany (de)
            United Kingdom (uk)
            France (fr)
        ]

    <div>
         <h2>5. Country</h2>
         <blockquote>Where are you from?</blockquote>
         <select name="country">
            <option selected="selected" value="">Please select</option>
            <option value="de">Germany</option>
            <option value="uk">United Kingdom</option>
            <option value="fr">France</option>
         </select>
    </div>

Note that a neutral "Please select" element will automatically be inserted to the top of the list.

### Value Matrix
This is useful if you have many answers that are all on the same scale.

    10. Programming Languages (other_languages_matrix) *
        How well do you know the following languages? 
        { No experience (0) -- Basic Knowledge (1) -- Expert (2) }
        [
            Java (java)
            C (c)
            C++ (cpp)
            VB.NET (vbnet)
            JavaScript (js)
            F# (fsharp)
        ]

    <div>
        <h2>10. Programming Languages</h2>
        <blockquote>How well do you know the following languages?</blockquote>
        <table>
            <thead><tr><th></th>
                <th>No experience</th>
                <th>Basic Knowledge</th>
                <th>Expert</th>
            </tr></thead>
            <tbody>
                <tr>
                    <td>Java</td>
                    <td><input type="radio" name="java" value="0" required></td>
                    <td><input type="radio" name="java" value="1" required></td>
                    <td><input type="radio" name="java" value="2" required></td>
                </tr>
                <tr>
                    <td>C</td>
                    <td><input type="radio" name="c" value="0" required></td>
                    <td><input type="radio" name="c" value="1" required></td>
                    <td><input type="radio" name="c" value="2" required></td>
                </tr>

                <!-- rest of the rows ommited-->

            </tbody>
        </table>
    </div>