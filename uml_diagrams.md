https://www.plantuml.com/

# class
@startuml
!define RECTANGLE class
skinparam linetype ortho
skinparam padding 5
skinparam roundcorner 5
skinparam class {
    BackgroundColor white
    ArrowColor black
    BorderColor black
}
RECTANGLE Piece {
}

RECTANGLE ZoneChecker {
}

RECTANGLE SolverManager {
}

RECTANGLE SolutionValidator {
}

RECTANGLE GridPolyminoGenerator {
}

RECTANGLE Plateau {
}

RECTANGLE MultiHeuristicManager {
}

RECTANGLE ConstraintMatrixBuilder {
}

RECTANGLE AlgorithmStats {
}

RECTANGLE AlgorithmX {
}

RECTANGLE IQPuzzlerInterface {
}

ZoneChecker o--> Plateau
ZoneChecker o--> Piece

SolverManager *--> AlgorithmX
SolverManager o--> Plateau 
SolverManager o--> Piece

SolutionValidator o--> Plateau
SolutionValidator o--> Piece

GridPolyminoGenerator *--> Piece

MultiHeuristicManager *--> SolverManager
MultiHeuristicManager o--> Plateau
MultiHeuristicManager o--> Piece

ConstraintMatrixBuilder o--> Plateau
ConstraintMatrixBuilder o--> Piece

AlgorithmX *--> AlgorithmStats
AlgorithmX *--> ConstraintMatrixBuilder
AlgorithmX *--> ZoneChecker
AlgorithmX *--> SolutionValidator
AlgorithmX o--> Plateau
AlgorithmX o--> Piece 

IQPuzzlerInterface *--> SolverManager
IQPuzzlerInterface *--> MultiHeuristicManager
IQPuzzlerInterface o--> Plateau
IQPuzzlerInterface o--> Piece
@enduml


# seq
@startuml
title IQ Solver Pro - Séquence de résolution

actor User
participant "IQPuzzlerInterface" as UI
participant "SolverManager" as SM
participant "AlgorithmX" as AX
participant "Plateau" as PL
participant "ConstraintMatrixBuilder" as CMB
participant "ZoneChecker" as ZC
participant "Piece" as PC 
participant "SolutionValidator" as SV
participant "AlgorithmStats" as AS

User -> UI: Place les pièces
User -> UI: start_resolution()
activate UI

    UI -> SM: run()
    activate SM
    
    SM -> AX: solve()
    activate AX
    
    AX -> CMB: create_constraint_matrix()
    activate CMB
    CMB -> PL: peut_placer()
    CMB --> AX: matrix, header
    deactivate CMB
    
    loop until solution found
        AX -> AX: algorithm_x()
        AX -> ZC: has_unfillable_voids()
        activate ZC
        ZC -> PL: apply_solution()
        ZC --> AX: result
        deactivate ZC
        
        AX -> AS: update_stats()
        
        alt solution found
            AX -> SV: validate_solution()
            activate SV
            SV -> PL: verify_placement()
            SV --> AX: is_valid
            deactivate SV
        end
    end
    
    AX --> SM: solution
    deactivate AX
    
    SM --> UI: update_display()
    deactivate SM


UI --> User: display_solution()
deactivate UI
@enduml