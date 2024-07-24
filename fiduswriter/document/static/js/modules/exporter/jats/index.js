import download from "downloadjs"
import pretty from "pretty"

import {shortFileTitle} from "../../common"
import {createSlug} from "../tools/file"
import {removeHidden} from "../tools/doc_content"
import {JATSExporterConvert} from "./convert"
import {JATSExporterCitations} from "./citations"
import {ZipFileCreator} from "../tools/zip"
import {darManifest} from "./templates"
/*
 Exporter to JATS
*/

export class JATSExporter {
    constructor(doc, bibDB, imageDB, csl, updated, type) {
        this.doc = doc
        this.docTitle = shortFileTitle(this.doc.title, this.doc.path)
        this.bibDB = bibDB
        this.imageDB = imageDB
        this.csl = csl
        this.updated = updated
        this.type = type // "article", "book-part-wrapper" (for documents) or "book" (for document collections)

        this.docContent = false
        this.zipFileName = false
        this.textFiles = []
        this.httpFiles = []
    }

    init() {
        const fileFormat = this.type === "article" ? "jats" : "bits"
        this.zipFileName = `${createSlug(this.docTitle)}.${fileFormat}.zip`
        this.docContent = removeHidden(this.doc.content)
        this.converter = new JATSExporterConvert(this, this.imageDB, this.bibDB, this.doc.settings)
        this.citations = new JATSExporterCitations(this, this.bibDB, this.csl)
        return this.converter.init(this.docContent).then(({jats, imageIds}) => {
            this.textFiles.push({filename: "manuscript.xml", contents: pretty(jats, {ocd: true})})
            const images = imageIds.map(
                id => {
                    const imageEntry = this.imageDB.db[id]
                    return {
                        title: imageEntry.title,
                        filename: imageEntry.image.split("/").pop(),
                        url: imageEntry.image
                    }
                }
            )
            this.textFiles.push({
                filename: "manifest.xml",
                contents: pretty(darManifest({title: this.docTitle, type: this.type, images}), {ocd: true})
            })
            images.forEach(image => {
                this.httpFiles.push({filename: image.filename, url: image.url})
            })

            return this.createZip()
        })
    }

    createZip() {
        const zipper = new ZipFileCreator(
            this.textFiles,
            this.httpFiles,
            undefined,
            undefined,
            this.updated
        )
        return zipper.init().then(
            blob => this.download(blob)
        )
    }

    download(blob) {
        return download(blob, this.zipFileName, "application/zip")
    }
}
