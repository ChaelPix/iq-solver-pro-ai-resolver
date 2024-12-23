https://www.plantuml.com/

<!-- TOC -->

- [seq](#seq)
- [seq 2](#seq-2)

<!-- /TOC -->

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
participant "Piece" as PC 
participant "Plateau" as PL
participant "SolverManager" as SM
participant "AlgorithmX" as AX
participant "ConstraintMatrixBuilder" as CMB
participant "ZoneChecker" as ZC
participant "SolutionValidator" as SV
participant "AlgorithmStats" as AS

UI->PL : Plateau(5,11)
User -> UI: Place les pièces
UI -> PC: get_piece()
PC --> UI: piece
UI -> PL: peut_placer()

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
    
    SM -> AS: get_stats()
    AS --> SM: stats
 
    SM --> UI: update_display()
    deactivate SM


UI --> User: display_solution()
deactivate UI
@enduml

# seq 2
@startuml
title IQ Solver Pro - Séquence de résolution

actor User
participant "IQPuzzlerInterface" as UI
participant "Piece" as PC 
participant "Plateau" as PL
participant "SolverManager" as SM

UI->PL : Plateau(5,11)
User -> UI: Place les pièces
UI -> PC: get_piece()
PC --> UI: piece
UI -> PL: peut_placer()

User -> UI: start_resolution()
activate UI
    UI -> SM: run()
    activate SM
    

    SM -> SM: gestion algo
 
    SM --> UI: update_display()
    deactivate SM


UI --> User: display_solution()
deactivate UI
@enduml