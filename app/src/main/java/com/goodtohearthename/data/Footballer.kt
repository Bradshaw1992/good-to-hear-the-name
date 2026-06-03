package com.goodtohearthename.data

import kotlinx.serialization.Serializable

@Serializable
data class Footballer(
    val id: String,
    val name: String,
    val country: String,
    val countryFlag: String,
    val years: String = "",
    val aliases: List<String> = emptyList(),
    val clues: List<String> = emptyList(),
    val image: String,
    val silhouette: String = "",
    val position: String = "",
    val yearsActive: String = "",
    val story: String = "",
    val clubs: List<String> = emptyList(),
    val honours: List<String> = emptyList(),
    val numbers: String = "",
    val didYouKnow: List<String> = emptyList(),
    val youtube: String? = null,
    val todayMatch: String? = null,
)

@Serializable
data class ContentFile(
    val footballers: List<Footballer>,
)

@Serializable
data class NameEntry(
    val n: String,            // name
    val f: String = "",       // flag emoji
    val y: String = "",       // active years e.g. "1997-2017"
)
