(forall (?l - location)
    (imply 
        (and (at {dangerou_name} ?l) (at {living_name} ?l)) 
        (at {container_name})
    )
)