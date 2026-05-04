package com.goodtohearthename.data

import kotlinx.serialization.Serializable

@Serializable
data class Footballer(
    val id: String,
    val name: String,
    val country: String,
    val countryFlag: String,
    val position: String,
    val yearsActive: String,
    val image: String,
    val story: String,
    val clubs: List<String>,
    val honours: List<String>,
    val numbers: String,
    val didYouKnow: List<String>,
    val youtube: String? = null,
)

@Serializable
data class ContentFile(
    val footballers: List<Footballer>,
)
