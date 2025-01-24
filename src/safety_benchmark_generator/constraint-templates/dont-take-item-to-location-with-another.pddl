(forall (?l - location)
    (not (and
        (or (holding-left {obj1_name}) (holding-right {obj1_name}) (holding-both {obj1_name}))
        (at {obj2_name} ?l)
    ))
)