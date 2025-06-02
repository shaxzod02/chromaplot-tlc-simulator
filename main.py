from fastapi import FastAPI
from fastapi import Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

import base64
import uuid
from pydantic import BaseModel, Field

from classes.compound import Compound
from classes.chromaplot import ChromaPlot


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# class Compound:

#     def __init__(self, name: str, x_cord: int, y_cord: int, ret_fact: float):

#         self.name = name    
#         self.x_cord = x_cord
#         self.y_cord = y_cord
#         self.ret_fact = ret_fact

class CompoundBase(BaseModel):
    compound_name: str = Field(..., min_length=1, max_length=15, description="Name of the compound")
    compound_ret_fact: float = Field(..., gt=0, min_length=2, description="Retention Factor of the compound")


@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("templates/index.html", "r") as f:
        html_content = f.read()
    return html_content

@app.post("/submit")
def submit_form(
    compound1_description: str = Form(...),
    compound1_rf: float = Form(...),
    compound2_description: str = Form(...),
    compound2_rf: float = Form(...),
    compound3_description: str = Form(...),
    compound3_rf: float = Form(...),
    compound4_description: str = Form(...),
    compound4_rf: float = Form(...),
    compound5_description: str = Form(...),
    compound5_rf: float = Form(...),
):
    # generate Compound class for each compound given by the user.

    solvent = Compound("solvent", 0, 0, 1.0)
    comp1 = Compound(f"{compound1_description}", 1, 0, compound1_rf)
    comp2 = Compound(f"{compound2_description}", 2, 0, compound2_rf)
    comp3 = Compound(f"{compound3_description}", 3, 0, compound3_rf)
    comp4 = Compound(f"{compound4_description}", 4, 0, compound4_rf)
    comp5 = Compound(f"{compound5_description}", 5, 0, compound5_rf)

    compounds = [solvent, comp1, comp2, comp3, comp4, comp5]
    compound_descs = [comp.name for comp in compounds]

    # generate a unique id for chromaplot
    plot_id = str(uuid.uuid4())

    # generate chromaplot 
    chroma_plot = ChromaPlot(compounds=compounds)
    chroma_plot.set_x_ticks(compound_descs)
    buffer = chroma_plot.generate_chromaplot()
    img_bytes = buffer.getvalue()

    with open(f"user_plots/{plot_id}.gif", "wb") as file:
        file.write(img_bytes)
    base64_img = base64.b64encode(img_bytes).decode("utf-8")
    return JSONResponse(content={"image": base64_img, "plot_id": plot_id})
    
@app.get("/download/{plot_id}", response_class=FileResponse)
def download_chomaplot(plot_id: str):

    # open and try to get the plot from dir
    try:
        user_plot_file_path = f"user_plots/{plot_id}.gif"
        return FileResponse(
            path=user_plot_file_path, 
            media_type="image/gif", 
            filename=f"{plot_id}.gif")
    except FileNotFoundError:
        return None




