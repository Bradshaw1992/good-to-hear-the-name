#!/usr/bin/env swift
//
// silhouette.swift — generate a black-figure-on-original-background silhouette
//   from an input photo using Apple Vision person segmentation.
//
// Usage:
//   swift scripts/silhouette.swift <input> <output>
//

import Foundation
import Vision
import CoreImage
import CoreImage.CIFilterBuiltins
import AppKit

let args = CommandLine.arguments
guard args.count == 3 else {
    print("Usage: swift silhouette.swift <input> <output>")
    exit(1)
}

let inputPath = args[1]
let outputPath = args[2]

guard let inputImage = CIImage(contentsOf: URL(fileURLWithPath: inputPath)) else {
    print("ERROR: cannot read input image \(inputPath)")
    exit(1)
}

let inputExtent = inputImage.extent

let request = VNGeneratePersonSegmentationRequest()
request.qualityLevel = .accurate
request.outputPixelFormat = kCVPixelFormatType_OneComponent8

let handler = VNImageRequestHandler(ciImage: inputImage, options: [:])
do {
    try handler.perform([request])
} catch {
    print("ERROR: segmentation failed: \(error)")
    exit(1)
}

guard let mask = request.results?.first else {
    print("ERROR: no segmentation mask produced")
    exit(1)
}

var maskImage = CIImage(cvPixelBuffer: mask.pixelBuffer)

// Scale mask to match input dimensions
let scaleX = inputExtent.width / maskImage.extent.width
let scaleY = inputExtent.height / maskImage.extent.height
maskImage = maskImage.transformed(by: CGAffineTransform(scaleX: scaleX, y: scaleY))

// Solid black layer matching input
let blackLayer = CIImage(color: CIColor.black).cropped(to: inputExtent)

// Composite: black over person, original background preserved
let blendFilter = CIFilter.blendWithMask()
blendFilter.inputImage = blackLayer
blendFilter.backgroundImage = inputImage
blendFilter.maskImage = maskImage

guard let output = blendFilter.outputImage?.cropped(to: inputExtent) else {
    print("ERROR: blend failed")
    exit(1)
}

let context = CIContext()
guard let cgImage = context.createCGImage(output, from: inputExtent) else {
    print("ERROR: CGImage failed")
    exit(1)
}

let rep = NSBitmapImageRep(cgImage: cgImage)
guard let data = rep.representation(using: .jpeg, properties: [.compressionFactor: 0.85]) else {
    print("ERROR: jpeg encoding failed")
    exit(1)
}

do {
    try data.write(to: URL(fileURLWithPath: outputPath))
} catch {
    print("ERROR: write failed: \(error)")
    exit(1)
}
