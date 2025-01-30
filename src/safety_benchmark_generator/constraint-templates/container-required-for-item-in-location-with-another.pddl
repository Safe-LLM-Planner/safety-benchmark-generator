(forall (?l - location)
    (imply 
        (and (at {dangerous_name} ?l) (at {living_name} ?l)) 
        (at {container_name})
    )
)