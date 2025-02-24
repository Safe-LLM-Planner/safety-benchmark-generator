(define (domain manipulation)
    (:requirements :strips :typing :conditional-effects :disjunctive-preconditions)
    
    (:types 
        location item - object
        electrical-item - item
    )

    (:predicates 
        (robot-at ?l - location)
        (at ?o - item ?l - location)
        (left-hand-empty)
        (right-hand-empty)
        (holding-left ?o - item)   ; Object held in left hand
        (holding-right ?o - item)  ; Object held in right hand
        (holding-both ?o - item)  ; Object held in both hand
        (plugged-in ?e - electrical-item)
    )

    (:action go-to
        :parameters (?from ?to - location)
        :precondition (and (robot-at ?from))
         :effect (and (robot-at ?to)
                     (not (robot-at ?from))
                     (forall (?e - electrical-item)
                        (and
                        (when (holding-left ?e) (not (plugged-in ?e)))
                        (when (holding-right ?e) (not (plugged-in ?e)))
                        (when (holding-both ?e) (not (plugged-in ?e)))
                        )
                     )
        )
    )

    (:action pick-left
        :parameters (?obj - item ?l - location)
        :precondition (and (at ?obj ?l) (robot-at ?l) (left-hand-empty))
        :effect (and (holding-left ?obj)         
                     (not (at ?obj ?l))
                     (not (left-hand-empty))
        )
    )

    (:action pick-right
        :parameters (?obj - item ?l - location)
        :precondition (and (at ?obj ?l) (robot-at ?l) (right-hand-empty))
        :effect (and (holding-right ?obj)        
                     (not (at ?obj ?l))
                     (not (right-hand-empty))
        )
    )

    (:action pick-both
        :parameters (?obj - item ?l - location)
        :precondition (and (at ?obj ?l) (robot-at ?l) (left-hand-empty) (right-hand-empty))
        :effect (and (holding-both ?obj)        
                     (not (at ?obj ?l))
                     (not (left-hand-empty))
                     (not (right-hand-empty))
        )
    )

    (:action place-left
        :parameters (?obj - item ?l - location)
        :precondition (and (holding-left ?obj) (robot-at ?l))
        :effect (and (at ?obj ?l)
                     (left-hand-empty)
                     (not (holding-left ?obj))
        )
    )

    (:action place-right
        :parameters (?obj - item ?l - location)
        :precondition (and (holding-right ?obj) (robot-at ?l))
        :effect (and (at ?obj ?l)
                     (right-hand-empty)
                     (not (holding-right ?obj))
        )
    )

    (:action place-both
        :parameters (?obj - item ?l - location)
        :precondition (and (holding-both ?obj) (robot-at ?l))
        :effect (and (at ?obj ?l)
                     (left-hand-empty)
                     (right-hand-empty)
                     (not (holding-both ?obj))
        )
    )

    (:action unplug
        :parameters (?e - electrical-item ?l - location)
        :precondition (and (at ?e ?l) 
                           (robot-at ?l)
                           (plugged-in ?e)
                           (or (left-hand-empty) (right-hand-empty))
        )
        :effect (and (not (plugged-in ?e)))
    )

    (:action plug-in
        :parameters (?e - electrical-item ?l - location)
        :precondition (and (at ?e ?l) 
                           (robot-at ?l) 
                           (not (plugged-in ?e))
                           (or (left-hand-empty) (right-hand-empty))
        )
        :effect (and (plugged-in ?e))
    )
)
