import vector_db
import pdf_splitter

vector_db = vector_db.VectorDatabase("mental_health_db")
pdf_process = pdf_splitter.PDFProcessor("../data/mental_health")
processed_pdf = pdf_process.run()
vector_db.create_db(processed_pdf)