"""Run with KiCad's Python after 'pcb import' to preserve project links and A2 stack."""
from pathlib import Path
import uuid
import pcbnew as pcb

folder = Path(__file__).resolve().parent
board_path = folder/"LNA.kicad_pcb"
board = pcb.LoadBoard(str(board_path))
settings = board.GetDesignSettings()
settings.SetBoardThickness(pcb.FromMM(.8))
sheet_id = uuid.uuid5(uuid.NAMESPACE_URL, "radio-telescope/LNA")
library = folder/"RT.pretty"
library.mkdir(exist_ok=True)
saved = set()
for footprint in board.GetFootprints():
    ref = footprint.GetReference()
    kind = str(footprint.GetFPID().GetLibItemName())
    footprint.SetFPIDAsString("RT:"+kind)
    footprint.SetPath(pcb.KIID_PATH("/"+str(uuid.uuid5(sheet_id,ref))))
    if kind not in saved:
        template = pcb.FOOTPRINT(footprint)
        template.SetReference("REF**")
        template.SetValue(kind)
        pcb.PCB_IO_KICAD_SEXPR().FootprintSave(str(library), template)
        saved.add(kind)
for net in board.GetNetInfo().NetsByName().values():
    if net.GetNetname():
        net.SetNetname("/"+net.GetNetname())
pcb.SaveBoard(str(board_path), board)
