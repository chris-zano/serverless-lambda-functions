const base64UrlDecode = (base64Url) => {
    // Convert from Base64 URL to standard Base64 by replacing URL-specific characters
    let base64 = base64Url
        .replace(/-/g, '+')
        .replace(/_/g, '/');

    while (base64.length % 4) {
        base64 += '='; // Add padding
    }
    // Decode the Base64 string to a UTF-8 string using atob
    return decodeURIComponent(
        atob(base64)
            .split('')
            .map((char) => `%${`00${char.charCodeAt(0).toString(16)}`.slice(-2)}`)
            .join('')
    );
};

const decodeJWT = (token) => {
    try {
        // Split the JWT into its three parts
        const [header, payload, signature] = token.split('.');
        if (!header || !payload || !signature) {
            throw new Error('Invalid JWT token structure');
        }
        // Decode the Base64 URL encoded header and payload
        const decodedHeader = base64UrlDecode(header);
        const decodedPayload = base64UrlDecode(payload);
        // Parse the JSON strings into objects
        const parsedHeader = JSON.parse(decodedHeader);
        const parsedPayload = JSON.parse(decodedPayload);
        // Return the decoded header and payload
        console.log({parsedHeader, parsedPayload})
        return {
            header: parsedHeader,
            payload: parsedPayload,
        };
    } catch (error) {
        console.error('Error decoding JWT:', error.message);
        return null;
    }
};

decodeJWT("")