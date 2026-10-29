# Merge notes

A conflicted file is not broken, it is a question. Git writes three markers into it:

    <<<<<<< HEAD
    your version
    =======
    their version
    >>>>>>> feat/x

(Indented on purpose - this is documentation, not a merge in progress.)

In a real conflicted file the markers always start in column 1.
