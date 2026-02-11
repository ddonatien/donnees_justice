use anyhow::{Context, Result};
use glob::glob;
use polars::prelude::*;
use quick_xml::de::from_str;
use serde::Deserialize;
use std::path::Path;
use regex::Regex;

fn default_string() -> String {
    "Unknown".to_string()
}

#[derive(Debug, Deserialize, PartialEq)]
struct Document {
    #[serde(rename = "Donnees_Techniques")]
    donnees_techniques: DonneesTechniques,
    
    #[serde(rename = "Dossier")]
    dossier: Dossier,
}

#[derive(Debug, Deserialize, PartialEq)]
struct DonneesTechniques {
    #[serde(rename = "Identification", default = "default_string")]
    identification: String,
    
    #[serde(rename = "Date_Mise_Jour", default = "default_string")]
    date_mise_jour: String,
}

#[derive(Debug, Deserialize, PartialEq)]
struct Dossier {
    #[serde(rename = "Code_Juridiction", default = "default_string")]
    code_juridiction: String,
    
    #[serde(rename = "Nom_Juridiction", default = "default_string")]
    nom_juridiction: String,
    
    #[serde(rename = "Numero_Dossier", default = "default_string")]
    numero_dossier: String,
    
    #[serde(rename = "Date_Lecture", default = "default_string")]
    date_lecture: String,
    
    #[serde(rename = "Type_Decision", default = "default_string")]
    type_decision: String,
    
    #[serde(rename = "Type_Recours", default = "default_string")]
    type_recours: String,
    
    #[serde(rename = "Code_Publication", default = "default_string")]
    code_publication: String,
    
    #[serde(rename = "Solution", default = "default_string")]
    solution: String,
}

fn parse_xml_file(xml_content: &str) -> Result<Document> {
    from_str(xml_content)
        .context("Failed to parse XML document")
}

fn read_xml_file(file_path: &Path) -> Result<String> {
    std::fs::read_to_string(file_path)
        .context(format!("Failed to read file: {}", file_path.display()))
}

fn process_xml_files(xml_files: Vec<String>) -> Result<Vec<Document>> {
    let mut documents = Vec::new();
    
    for file_path in xml_files {
        let path = Path::new(&file_path);
        // Print file path if read_xml_file fails
        let xml_content = read_xml_file(path)
            .context(format!("Error reading XML file: {}", file_path))?;
        // Print file path if parse_xml_file fails
        let document = parse_xml_file(&xml_content)
            .context(format!("Error parsing XML file: {}", file_path))?;
        documents.push(document);
    }
    
    Ok(documents)
}

fn find_xml_files(data_dir: &str) -> Result<Vec<String>> {
    let pattern = format!("{}/**/*.xml", data_dir);
    let mut xml_files = Vec::new();
    
    for entry in glob(&pattern)? {
        match entry {
            Ok(path) => xml_files.push(path.display().to_string()),
            Err(e) => return Err(anyhow::anyhow!(e)),
        }
    }
    
    Ok(xml_files)
}

fn create_dataframe(documents: Vec<Document>) -> Result<DataFrame> {
    let mut identification = Vec::new();
    let mut date_mise_jour = Vec::new();
    let mut source = Vec::new();
    let mut code_juridiction = Vec::new();
    let mut nom_juridiction = Vec::new();
    let mut numero_dossier = Vec::new();
    let mut date_lecture = Vec::new();
    let mut type_decision = Vec::new();
    let mut type_recours = Vec::new();
    let mut code_publication = Vec::new();
    let mut solution = Vec::new();

    let re = Regex::new(r"[A-Z]+")?;

    for doc in documents {
        date_mise_jour.push(doc.donnees_techniques.date_mise_jour);
        identification.push(doc.donnees_techniques.identification);
        source.push(re.find(&doc.dossier.code_juridiction)
            .map_or("Unknown".to_string(), |m| m.as_str().to_string()));
        code_juridiction.push(doc.dossier.code_juridiction);
        nom_juridiction.push(doc.dossier.nom_juridiction);
        numero_dossier.push(doc.dossier.numero_dossier);
        date_lecture.push(doc.dossier.date_lecture);
        type_decision.push(doc.dossier.type_decision);
        type_recours.push(doc.dossier.type_recours);
        code_publication.push(doc.dossier.code_publication);
        solution.push(doc.dossier.solution);
    }
    
    let df = DataFrame::new(vec![
        Series::new("Identification", identification),
        Series::new("Date_Mise_Jour", date_mise_jour),
        Series::new("Source", source),
        Series::new("Code_Juridiction", code_juridiction),
        Series::new("Nom_Juridiction", nom_juridiction),
        Series::new("Numero_Dossier", numero_dossier),
        Series::new("Date_Lecture", date_lecture),
        Series::new("Type_Decision", type_decision),
        Series::new("Type_Recours", type_recours),
        Series::new("Code_Publication", code_publication),
        Series::new("Solution", solution),
    ])?;
    
    Ok(df)
}

fn save_to_parquet(df: &mut DataFrame, output_path: &str) -> Result<()> {
    let file = std::fs::File::create(output_path)
        .context("Failed to create output file")?;
    
    ParquetWriter::new(file)
        .finish(df)
        .context("Failed to write Parquet file")?;
    
    Ok(())
}

fn main() -> Result<()> {
    // Configuration - in production this would come from config files
    let data_dir = "data/raw";
    let output_file = "data/clean/court_decisions.parquet";
    
    println!("Ingesting files. This may take a while... ⏳ (5mins)");
    println!("🔍 Finding XML files in: {}", data_dir);
    let xml_files = find_xml_files(data_dir)?;
    println!("📁 Found {} XML files", xml_files.len());
    
    if xml_files.is_empty() {
        println!("⚠️  No XML files found in the data directory");
        return Ok(());
    }
    
    println!("📖 Processing XML files...");
    let documents = process_xml_files(xml_files)?;
    println!("✅ Successfully parsed {} documents", documents.len());
    
    println!("📊 Creating DataFrame...");
    let mut df = create_dataframe(documents)?;
    println!("📈 DataFrame created with {} rows and {} columns", 
             df.height(), df.width());
    
    println!("💾 Saving to Parquet: {}", output_file);
    save_to_parquet(&mut df, output_file)?;
    println!("✅ Successfully saved Parquet file");
    
    Ok(())
}
